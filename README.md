# GGPoker hand history parser

A python program that parses GGPoker hand histories for further analysis and examination.

Hand history formatting example:
```
Poker Hand #HD2258209222: Hold'em No Limit ($0.01/$0.02) - 2025/04/09 22:13:05
Table 'NLHWhite52' 6-max Seat #1 is the button
Seat 1: Hero ($1.77 in chips)
Seat 2: 626f7725 ($4.57 in chips)
Seat 3: 7a13c8e8 ($3.68 in chips)
Seat 4: 4fe80d07 ($2.37 in chips)
Seat 5: 9b730ead ($2.35 in chips)
Seat 6: 5d2079a8 ($2 in chips)
626f7725: posts small blind $0.01
7a13c8e8: posts big blind $0.02
*** HOLE CARDS ***
Dealt to Hero [4c Js]
Dealt to 626f7725 
Dealt to 7a13c8e8 
Dealt to 4fe80d07 
Dealt to 9b730ead 
Dealt to 5d2079a8 
4fe80d07: folds
9b730ead: folds
5d2079a8: folds
Hero: folds
626f7725: raises $0.04 to $0.06
7a13c8e8: calls $0.04
*** FLOP *** [Ks 8d 5h]
626f7725: checks
7a13c8e8: bets $0.07
626f7725: raises $0.21 to $0.28
7a13c8e8: calls $0.21
*** TURN *** [Ks 8d 5h] [Jc]
626f7725: bets $0.4
7a13c8e8: calls $0.4
*** RIVER *** [Ks 8d 5h Jc] [2d]
626f7725: checks
7a13c8e8: checks
626f7725: shows [7d 4d] (King high)
7a13c8e8: shows [Ah 8c] (a pair of Eights)
*** SHOWDOWN ***
7a13c8e8 collected $1.39 from pot
*** SUMMARY ***
Total pot $1.48 | Rake $0.07 | Jackpot $0.02 | Bingo $0 | Fortune $0 | Tax $0
Board [Ks 8d 5h Jc 2d]
Seat 1: Hero (button) folded before Flop (didn't bet)
Seat 2: 626f7725 (small blind) showed [7d 4d] and lost with King high
Seat 3: 7a13c8e8 (big blind) showed [Ah 8c] and won ($1.39) with a pair of Eights
Seat 4: 4fe80d07 folded before Flop (didn't bet)
Seat 5: 9b730ead folded before Flop (didn't bet)
Seat 6: 5d2079a8 folded before Flop (didn't bet)
```