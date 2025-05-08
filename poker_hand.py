import re

class PokerHand:
    def __init__(self, hand_history):
        self.hand_history = hand_history
        self.lines = [line.strip() for line in hand_history.split('\n') if line.strip()]
        self.hand_info = {}
        self.players = []
        self.blinds = []
        self.hero_cards = []
        self.actions = {
            'preflop': [],
            'flop': [],
            'turn': [],
            'river': [],
            'showdown': []
        }
        self.board = []
        self.summary = {
            'total_pot': 0.0,
            'rake': 0.0,
            'board': [],
            'seat_results': []
        }
        self.current_section = None
        self._parse()

    def _parse(self):
        for line in self.lines:
            if line.startswith('Poker Hand #'):
                self._parse_header(line)
            elif line.startswith('Table'):
                self._parse_table(line)
            elif line.startswith('Seat') and not self.current_section == 'summary':
                self._parse_seat(line)
            elif any(x in line for x in ['posts small blind', 'posts big blind']):
                self._parse_blind(line)
            elif line.startswith('***'):
                self._parse_section_header(line)
            else:
                self._parse_line_content(line)

    def _parse_header(self, line):
        match = re.match(
            r'Poker Hand #(HD\d+): (.+?) \((\$[\d.]+/\$[\d.]+)\) - (\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})',
            line
        )
        if match:
            self.hand_info = {
                'hand_id': match.group(1),
                'game_type': match.group(2),
                'stakes': match.group(3),
                'date': match.group(4)
            }

    def _parse_table(self, line):
        match = re.match(
            r"Table '(.+?)' (\d+-max) Seat #(\d+) is the button",
            line
        )
        if match:
            self.hand_info.update({
                'table_name': match.group(1),
                'max_players': match.group(2),
                'button_seat': int(match.group(3))
            })

    def _parse_seat(self, line):
        match = re.match(
            r"Seat (\d+): (.+?) \(\$([\d.]+) in chips\)",
            line
        )
        if match:
            self.players.append({
                'seat': int(match.group(1)),
                'player': match.group(2),
                'stack': float(match.group(3))
            })

    def _parse_blind(self, line):
        match = re.match(
            r"(.+?): posts (small|big) blind \$([\d.]+)",
            line
        )
        if match:
            self.blinds.append({
                'player': match.group(1),
                'type': match.group(2),
                'amount': float(match.group(3))
            })

    def _parse_section_header(self, line):
        section_map = {
            'HOLE CARDS': 'preflop',
            'FLOP': 'flop',
            'TURN': 'turn',
            'RIVER': 'river',
            'SHOWDOWN': 'showdown',
            'SUMMARY': 'summary'
        }
        section = line.replace('***', '').strip().split()[0]
        self.current_section = section_map.get(section, None)
        
        # Parse board cards if present in section header
        if self.current_section in ['flop', 'turn', 'river']:
            cards = re.findall(r'\[(.*?)\]', line)
            if cards:
                new_cards = cards[0].split()
                if self.current_section == 'flop':
                    self.board = new_cards
                else:
                    self.board.extend(new_cards)
                self.summary['board'] = self.board

    def _parse_line_content(self, line):
        if self.current_section == 'preflop':
            if 'Dealt to Hero' in line:
                self._parse_hero_cards(line)
            else:
                self._parse_action(line, 'preflop')
        elif self.current_section in ['flop', 'turn', 'river', 'showdown']:
            if line.startswith('Uncalled bet'):
                self._parse_uncalled_bet(line, self.current_section)
            else:
                self._parse_action(line, self.current_section)
        elif self.current_section == 'summary':
            self._parse_summary(line)

    def _parse_hero_cards(self, line):
        cards = re.findall(r'\[(.*?)\]', line)
        if cards:
            self.hero_cards = cards[0].split()

    def _parse_action(self, line, street):
        action_patterns = [
            (r'(.+?): folds', 'fold'),
            (r'(.+?): checks', 'check'),
            (r'(.+?): calls \$([\d.]+)', 'call'),
            (r'(.+?): bets \$([\d.]+)', 'bet'),
            (r'(.+?): raises \$([\d.]+) to \$([\d.]+)', 'raise'),
            (r'(.+?) collected \$([\d.]+) from pot', 'collect')
        ]

        for pattern, action_type in action_patterns:
            match = re.match(pattern, line)
            if match:
                action = {'player': match.group(1), 'action': action_type}
                if action_type in ['call', 'bet']:
                    action['amount'] = float(match.group(2))
                elif action_type == 'raise':
                    action['amount'] = float(match.group(2))
                    action['total'] = float(match.group(3))
                elif action_type == 'collect':
                    action['amount'] = float(match.group(2))
                self.actions[street].append(action)
                return

    def _parse_uncalled_bet(self, line, street):
        match = re.match(r'Uncalled bet \(\$([\d.]+)\) returned to (.+)', line)
        if match:
            self.actions[street].append({
                'player': match.group(2),
                'action': 'uncalled_bet_return',
                'amount': float(match.group(1))
            })

    def _parse_summary(self, line):
        if line.startswith('Total pot'):
            self._parse_pot(line)
        elif line.startswith('Board'):
            self._parse_summary_board(line)
        elif line.startswith('Seat'):
            self._parse_seat_result(line)

    def _parse_pot(self, line):
        pot_match = re.search(r'Total pot \$([\d.]+)', line)
        rake_match = re.search(r'Rake \$([\d.]+)', line)
        if pot_match:
            self.summary['total_pot'] = float(pot_match.group(1))
        if rake_match:
            self.summary['rake'] = float(rake_match.group(1))

    def _parse_summary_board(self, line):
        cards = re.findall(r'\[(.*?)\]', line)
        if cards:
            self.summary['board'] = cards[0].split()

    def _parse_seat_result(self, line):
        match = re.match(
            r'Seat (\d+): (.+?) (folded|won|collected) (.*)',
            line
        )
        if match:
            self.summary['seat_results'].append({
                'seat': int(match.group(1)),
                'player': match.group(2),
                'result': match.group(3),
                'details': match.group(4)
            })
