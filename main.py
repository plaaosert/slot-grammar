import grammar as gr
import os


os.system("")


ruleset = gr.Ruleset(
    5, 5,
    {0: {
        "J": (1, 0.005), "Q": (1, 0.005), "K": (1, 0.005), "10": (1, 0.005),
        "Shoes": (0.3, 0.02), "Shirt": (0.3, 0.02), "Service": (0.3, 0.02), "WILD": (0.02, 0.022)
    }},
    False, 5, gr.MatchType.LTR,
    {0: {
        "J": ("J", "WILD"), "Q": ("Q", "WILD"), "K": ("K", "WILD"), "10": ("10", "WILD"),
        "Shoes": ("Shoes", "WILD"), "Shirt": ("Shirt", "WILD"), "Service": ("Service", "WILD"),
        "WILD": ("J", "Q", "K", "10", "Shoes", "Shirt", "Service", "WILD")
    }},
    [], [0], 0
)

board = gr.Board(ruleset)

# Calculate RTP
"""
avg = 0
times = 200000
for i in range(times):
    board.spin()
    avg += (board.value_matches(board.check_matches()) - avg) / (i + 1)

print("Average RTP is {}".format(avg))
"""

# "Game"
cash = 100000
print("\u001b[2;1H", end="")
board.render()
print("\n\n\n\n                  CASH:   {:8}".format(cash))
while True:
    input("")
    board.spin()
    print("\u001b[2;1H", end="")
    board.render()
    matches = board.check_matches()
    payout = int(board.value_matches(matches) * 1000)
    if payout > 0:
        print("\n                  {:6} ways!".format(len(matches)))
        # print("\n".join(str(t) for t in matches))
        print("                  PAYOUT: {:8}".format(payout))
    else:
        print("\n                                        \n                                        ")

    cash -= 1000
    cash += payout
    print("\n                  CASH:   {:8}".format(cash))

# Manual spinning
"""
board.render()
while True:
    input("")
    board.spin()
    board.render()
    matches = board.check_matches()
    print("\n" + str(len(matches)), "matches!")
    # print("\n".join(str(t) for t in matches))
    print("Value:", board.value_matches(matches))
"""
