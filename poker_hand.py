import re
from datetime import datetime

class PokerHand:
    def __init__(self, hand_history):
        self.hand_history = hand_history
        self.lines = hand_history.split('\n')
        self.parsed_data = {
            'hand_id': None,
            'game_type': None,
            'blinds': (0.0, 0.0),
            'date_time': None,
            'table_name': None,
            'max_players': 0,
            'button_seat': 0,
            'seats': [],
            'players': {},
            'blinds_posted': {'small_blind': None, 'big_blind': None},
            'hole_cards': {},
            'board': {
                'flop': [],
                'turn': [],
                'river': []
            },
            'streets': {
                'preflop': [],
                'flop': [],
                'turn': [],
                'river': []
            },
            'showdown': {},
            'pot': {
                'total': 0.0,
                'rake': 0.0,
                'jackpot': 0.0,
                'bingo': 0.0,
                'fortune': 0.0,
                'tax': 0.0,
                'net': 0.0
            }
        }
        self.current_street = None

    def parse(self):
        for line in self.lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('Poker Hand #'):
                self._parse_header(line)
            elif line.startswith('Table'):
                self._parse_table(line)
            elif line.startswith('Seat '):
                self._parse_seat(line)
            elif ': posts small blind' in line or ': posts big blind' in line:
                self._parse_blind(line)
            elif line.startswith('*** HOLE CARDS ***'):
                self.current_street = 'preflop'
            elif line.startswith('*** FLOP ***'):
                self.current_street = 'flop'
                self._parse_board(line)
            elif line.startswith('*** TURN ***'):
                self.current_street = 'turn'
                self._parse_board(line)
            elif line.startswith('*** RIVER ***'):
                self.current_street = 'river'
                self._parse_board(line)
            elif line.startswith('*** SHOWDOWN ***'):
                self.current_street = 'showdown'
            elif line.startswith('*** SUMMARY ***'):
                self.current_street = 'summary'
            elif line.startswith('Dealt to'):
                self._parse_hole_cards(line)
            elif self.current_street in ['preflop', 'flop', 'turn', 'river']:
                self._parse_action(line)
            elif self.current_street == 'showdown':
                self._parse_showdown(line)
            elif self.current_street == 'summary':
                if line.startswith('Total pot'):
                    self._parse_summary(line)
                elif line.startswith('Seat '):
                    self._parse_summary_seat(line)
        self._determine_positions()

    def _parse_header(self, line):
        header_pattern = re.compile(
            r"Poker Hand #(\w+): (.+?) \((\$[\d.]+)/(\$[\d.]+)\) - (\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})"
        )
        match = header_pattern.match(line)
        if match:
            self.parsed_data['hand_id'] = match.group(1)
            self.parsed_data['game_type'] = match.group(2)
            sb = float(match.group(3).replace('$', ''))
            bb = float(match.group(4).replace('$', ''))
            self.parsed_data['blinds'] = (sb, bb)
            date_str = match.group(5)
            self.parsed_data['date_time'] = datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')

    def _parse_table(self, line):
        table_pattern = re.compile(
            r"Table '([^']+)' (\d+)-max Seat #(\d+) is the button"
        )
        match = table_pattern.match(line)
        if match:
            self.parsed_data['table_name'] = match.group(1)
            self.parsed_data['max_players'] = int(match.group(2))
            self.parsed_data['button_seat'] = int(match.group(3))

    def _parse_seat(self, line):
        seat_pattern = re.compile(
            r"Seat (\d+): ([^ ]+) \(\$([\d.]+) in chips\)"
        )
        match = seat_pattern.match(line)
        if match:
            seat_num = int(match.group(1))
            player = match.group(2)
            stack = float(match.group(3))
            self.parsed_data['seats'].append({'seat': seat_num, 'player': player, 'stack': stack})
            self.parsed_data['players'][player] = {
                'seat': seat_num,
                'stack': stack,
                'position': None,
                'cards': [],
                'actions': {'preflop': [], 'flop': [], 'turn': [], 'river': []},
                'profit': 0.0,
                'hand_type': None
            }

    def _parse_blind(self, line):
        blind_pattern = re.compile(
            r"([^:]+): posts (small|big) blind \$([\d.]+)"
        )
        match = blind_pattern.match(line)
        if match:
            player = match.group(1)
            blind_type = match.group(2).lower()
            amount = float(match.group(3))
            self.parsed_data['blinds_posted'][f'{blind_type}_blind'] = player

    def _parse_hole_cards(self, line):
        hole_cards_pattern = re.compile(
            r"Dealt to ([^ ]+) (?:\[([^\]]*)\])?"
        )
        match = hole_cards_pattern.match(line)
        if match:
            player = match.group(1)
            cards_str = match.group(2)
            if cards_str:
                cards = cards_str.strip().split()
                self.parsed_data['players'][player]['cards'] = cards

    def _parse_board(self, line):
        board_pattern = re.compile(r"\[([^\]]+)\]")
        match = board_pattern.findall(line)
        if match:
            cards = flatten([elem.split() for elem in match])
            if self.current_street == 'flop':
                self.parsed_data['board']['flop'] = cards
            elif self.current_street == 'turn':
                self.parsed_data['board']['turn'] = cards
            elif self.current_street == 'river':
                self.parsed_data['board']['river'] = cards

    def _parse_action(self, line):
        action_pattern = re.compile(
            r"([^:]+): (folds|checks|calls|bets|raises) ?(\$?[\d.]*)?(?: to \$?([\d.]+))?"
        )
        match = action_pattern.match(line)
        if match:
            player = match.group(1)
            action = match.group(2)
            amount1 = match.group(3) or ''
            amount2 = match.group(4) or ''
            action_str = action
            if action == 'bets':
                amount = amount1.replace('$', '')
                action_str = f"{action} ${float(amount):.2f}"
            elif action in ['raises', 'calls']:
                amount = amount1.replace('$', '')
                if action == 'raises':
                    to_amount = amount2.replace('$', '')
                    action_str = f"{action} ${float(amount):.2f} to ${float(to_amount):.2f}"
                else:
                    action_str = f"{action} ${float(amount):.2f}"
            self.parsed_data['players'][player]['actions'][self.current_street].append(action_str)
            self.parsed_data['streets'][self.current_street].append({
                'player': player,
                'action': action_str
            })

    def _parse_showdown(self, line):
        show_pattern = re.compile(
            r"([^:]+): shows \[([^\]]+)\] \((.*)\)"
        )
        match = show_pattern.match(line)
        if match:
            player = match.group(1)
            cards = match.group(2).split()
            hand_type = match.group(3)
            self.parsed_data['showdown'][player] = {'cards': cards, 'hand_type': hand_type}
            self.parsed_data['players'][player]['hand_type'] = hand_type
            self.parsed_data['players'][player]['cards'] = cards

    def _parse_summary(self, line):
        pot_pattern = re.compile(
            r"Total pot \$([\d.]+) \| Rake \$([\d.]+) \| Jackpot \$([\d.]+) \| Bingo \$([\d.]+) \| Fortune \$([\d.]+) \| Tax \$([\d.]+)"
        )
        match = pot_pattern.search(line)
        if match:
            total = float(match.group(1))
            rake = float(match.group(2))
            jackpot = float(match.group(3))
            bingo = float(match.group(4))
            fortune = float(match.group(5))
            tax = float(match.group(6))
            self.parsed_data['pot'] = {
                'total': total,
                'rake': rake,
                'jackpot': jackpot,
                'bingo': bingo,
                'fortune': fortune,
                'tax': tax,
                'net': total - (rake + jackpot + bingo + fortune + tax)
            }

    def _parse_summary_seat(self, line):
        summary_seat_pattern = re.compile(
            r"Seat \d+: ([^ ]+) (?:\(([^)]+)\) )?(?:showed \[([^\]]*)\] and (lost|won) \((\$[\d.]+)\))?(?: with (.*))?"
        )
        match = summary_seat_pattern.match(line)
        if match:
            player = match.group(1)
            position = match.group(2)
            cards_str = match.group(3)
            result = match.group(4)
            amount_str = match.group(5)
            hand_type = match.group(6)
            if position:
                self.parsed_data['players'][player]['position'] = position
            if cards_str:
                self.parsed_data['players'][player]['cards'] = cards_str.split()
            if result and amount_str:
                amount = float(amount_str.replace('$', ''))
                if result == 'lost':
                    amount = -amount
                self.parsed_data['players'][player]['profit'] = amount
            if hand_type:
                self.parsed_data['players'][player]['hand_type'] = hand_type

    def _determine_positions(self):
        button_seat = self.parsed_data['button_seat']
        max_players = self.parsed_data['max_players']
        if max_players != 6:
            return
        positions_order = ['BU', 'SB', 'BB', 'UTG', 'HJ', 'CO']
        for seat in self.parsed_data['seats']:
            seat_num = seat['seat']
            player = seat['player']
            offset = (seat_num - button_seat) % max_players
            position = positions_order[offset]
            if self.parsed_data['players'][player]['position'] is None:
                self.parsed_data['players'][player]['position'] = position

    def get_parsed_data(self):
        return self.parsed_data
    
def flatten(xss):
    return [x for xs in xss for x in xs]
