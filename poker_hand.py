import re

class PokerHand:
    def __init__(self, hand_text):
        self.hand_text = hand_text
        self.parsed_data = {
            'hand_id': None,
            'date_time': None,
            'blinds': {'sb': None, 'bb': None},
            'button_seat': None,
            'table_size': None,
            'players': {},
            'streets': {
                'preflop': [],
                'flop': [],
                'turn': [],
                'river': []
            },
            'board': [],
            'preflop_aggressor': None,
            '3bet_pot': False,
            '4bet_pot': False,
            'c_bet': False,
            'donk_bet': False,
            'shown_cards': {},
            'hand_types': {},
            'pot_size': None,
            'rake': None,
            'jackpot': None,
            'profits': {}
        }
        self.current_street = None

    def parse(self):
        lines = self.hand_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('Poker Hand #'):
                self._parse_header(line)
            elif line.startswith('Table'):
                self._parse_table(line)
            elif line.startswith('Seat') and self.current_street is None:
                self._parse_initial_seat(line)
            elif '*** HOLE CARDS ***' in line:
                self.current_street = 'preflop'
            elif '*** FLOP ***' in line:
                self.current_street = 'flop'
                self._parse_board(line)
            elif '*** TURN ***' in line:
                self.current_street = 'turn'
                self._parse_board(line)
            elif '*** RIVER ***' in line:
                self.current_street = 'river'
                self._parse_board(line)
            elif '*** SHOWDOWN ***' in line:
                self.current_street = 'showdown'
            elif '*** SUMMARY ***' in line:
                self.current_street = 'summary'
            else:
                if self.current_street in ['preflop', 'flop', 'turn', 'river']:
                    self._parse_action(line)
                elif self.current_street == 'summary':
                    self._parse_summary_line(line)
                else:
                    if any(keyword in line for keyword in ['posts small blind', 'posts big blind']):
                        self._parse_blind_post(line)
                    elif 'Dealt to' in line:
                        self._parse_dealt_cards(line)
                    elif 'collected' in line and self.current_street != 'summary':
                        self._parse_collected(line)
                    elif ('shows' in line or 'mucks' in line) and self.current_street != 'summary':
                        self._parse_showdown(line)

        self._determine_preflop_aggressor()
        self._check_3bet_4bet()
        self._check_cbet_donkbet()
        return self.parsed_data

    def _parse_header(self, line):
        header_re = r'Poker Hand #(\w+): (.*?) \((.*?)\) - (\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})'
        match = re.match(header_re, line)
        if match:
            self.parsed_data['hand_id'] = match.group(1)
            blinds_str = match.group(3)
            sb, bb = blinds_str.replace('$', '').split('/')
            self.parsed_data['blinds']['sb'] = float(sb)
            self.parsed_data['blinds']['bb'] = float(bb)
            self.parsed_data['date_time'] = match.group(4)

    def _parse_table(self, line):
        parts = line.split()
        self.parsed_data['table_size'] = parts[2]
        button_seat = parts[-2].replace('#', '')
        self.parsed_data['button_seat'] = int(button_seat)

    def _parse_initial_seat(self, line):
        parts = re.match(r'Seat (\d+): (.*?) \(\$([\d.]+) in chips\)', line)
        if parts:
            seat_num = parts.group(1)
            player_name = parts.group(2)
            stack = float(parts.group(3))
            self.parsed_data['players'][player_name] = {
                'seat': seat_num,
                'stack': stack,
                'position': None,
                'hole_cards': None,
                'profit': 0.0,
                'hand_type': None
            }

    def _parse_blind_post(self, line):
        player = line.split(':')[0].strip()
        amount = float(re.findall(r'\$([\d.]+)', line)[0])
        if 'small blind' in line:
            self.parsed_data['players'][player]['position'] = 'SB'
        elif 'big blind' in line:
            self.parsed_data['players'][player]['position'] = 'BB'

    def _parse_dealt_cards(self, line):
        match = re.match(r'Dealt to (.*?) \[(.*?)\]', line)
        if match:
            player = match.group(1)
            cards = match.group(2).split()
            self.parsed_data['players'][player]['hole_cards'] = cards

    def _parse_action(self, line):
        player_part, action_part = line.split(': ', 1)
        player = player_part.strip()
        action = action_part.strip()
        self.parsed_data['streets'][self.current_street].append({'player': player, 'action': action})

    def _parse_summary_line(self, line):
        if line.startswith('Total pot'):
            parts = line.split('|')
            for part in parts:
                part = part.strip()
                if part.startswith('Total pot'):
                    self.parsed_data['pot_size'] = float(re.findall(r'\$([\d.]+)', part)[0])
                elif part.startswith('Rake'):
                    self.parsed_data['rake'] = float(re.findall(r'\$([\d.]+)', part)[0])
                elif part.startswith('Jackpot'):
                    self.parsed_data['jackpot'] = float(re.findall(r'\$([\d.]+)', part)[0])
        elif line.startswith('Seat'):
            seat_info = re.match(r'Seat \d+: (.*?)(?: \((.*?)\)|)(?: showed \[(.*?)\]|).*?(?:collected \$([\d.]+)|)', line)
            if seat_info:
                player = seat_info.group(1).strip()
                position = seat_info.group(2)
                cards = seat_info.group(3)
                amount = seat_info.group(4)
                if position:
                    if 'small blind' in position:
                        position = 'SB'
                    elif 'big blind' in position:
                        position = 'BB'
                    elif 'button' in position:
                        position = 'BU'
                    self.parsed_data['players'][player]['position'] = position
                if cards:
                    self.parsed_data['shown_cards'][player] = cards.split()
                if amount:
                    self.parsed_data['profits'][player] = float(amount)
                hand_type_match = re.search(r'with (.*?)\)', line)
                if hand_type_match:
                    self.parsed_data['hand_types'][player] = hand_type_match.group(1)

    def _parse_showdown(self, line):
        player_part, rest = line.split(':', 1)
        player = player_part.strip()
        if 'shows [' in rest:
            cards = rest.split('[')[1].split(']')[0].split()
            self.parsed_data['shown_cards'][player] = cards
            hand_type = rest.split('] ')[1].split('(')[-1].split(')')[0]
            self.parsed_data['hand_types'][player] = hand_type

    def _parse_collected(self, line):
        player = line.split(' collected')[0].strip()
        amount = float(re.findall(r'\$([\d.]+)', line)[0])
        self.parsed_data['profits'][player] = amount

    def _parse_board(self, line):
        cards = re.findall(r'\[(.*?)\]', line)
        if cards:
            new_cards = cards[-1].split()
            self.parsed_data['board'].extend(new_cards)

    def _determine_preflop_aggressor(self):
        for action in self.parsed_data['streets']['preflop']:
            if 'raises' in action['action']:
                self.parsed_data['preflop_aggressor'] = action['player']
                return

    def _check_3bet_4bet(self):
        raises = [a for a in self.parsed_data['streets']['preflop'] if 'raises' in a['action']]
        num_raises = len(raises)
        self.parsed_data['3bet_pot'] = num_raises >= 2
        self.parsed_data['4bet_pot'] = num_raises >= 3

    def _check_cbet_donkbet(self):
        aggressor = self.parsed_data['preflop_aggressor']
        if not aggressor:
            return
        flop_actions = self.parsed_data['streets']['flop']
        first_bet = None
        for action in flop_actions:
            if 'bets' in action['action']:
                first_bet = action['player']
                break
        if first_bet:
            if first_bet == aggressor:
                self.parsed_data['c_bet'] = True
            else:
                self.parsed_data['donk_bet'] = True