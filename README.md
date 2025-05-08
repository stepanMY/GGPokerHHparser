# GGPoker hand history parser

A python program that parses GGPoker hand histories for further analysis and examination.

Hand history formatting example:
```
Poker Hand #HD2255183008: Hold'em No Limit ($0.01/$0.02) - 2025/04/07 23:48:32
Table 'NLHWhite9' 6-max Seat #4 is the button
Seat 1: Hero ($1.64 in chips)
Seat 2: 9db941d0 ($1.5 in chips)
Seat 3: 7823be4b ($3.97 in chips)
Seat 4: 6c2a9622 ($1.95 in chips)
Seat 5: 23cee45e ($2.05 in chips)
Seat 6: be078c22 ($1.35 in chips)
23cee45e: posts small blind $0.01
be078c22: posts big blind $0.02
*** HOLE CARDS ***
Dealt to Hero [Qd 6c]
Dealt to 9db941d0 
Dealt to 7823be4b 
Dealt to 6c2a9622 
Dealt to 23cee45e 
Dealt to be078c22 
Hero: folds
9db941d0: raises $0.02 to $0.04
7823be4b: folds
6c2a9622: folds
23cee45e: folds
be078c22: calls $0.02
*** FLOP *** [2d 3h Kc]
be078c22: checks
9db941d0: bets $0.05
be078c22: folds
Uncalled bet ($0.05) returned to 9db941d0
*** SHOWDOWN ***
9db941d0 collected $0.09 from pot
*** SUMMARY ***
Total pot $0.09 | Rake $0 | Jackpot $0 | Bingo $0 | Fortune $0 | Tax $0
Board [2d 3h Kc]
Seat 1: Hero folded before Flop (didn't bet)
Seat 2: 9db941d0 won ($0.09)
Seat 3: 7823be4b folded before Flop (didn't bet)
Seat 4: 6c2a9622 (button) folded before Flop (didn't bet)
Seat 5: 23cee45e (small blind) folded before Flop
Seat 6: be078c22 (big blind) folded on the Flop
```