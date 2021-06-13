from cards import Card, Deck, Pile
from players import Player, Group, State


def setup_deck(shuffle=True):
    """
    Initialises the deck with all colour and wild cards, then shuffles it
    :param shuffle: Whether to shuffle the deck
    :type shuffle: bool
    :return: The deck in order
    :rtype: Deck
    """

    deck = Deck()

    # add colour cards
    for colour in ("R", "G", "B", "Y"):
        # add number cards
        deck.add(Card(colour, number=0))
        for i in range(9):
            deck.add(Card(colour, number=i+1), quantity=2)
        # add action cards
        deck.add(Card(colour, action="+2"), quantity=2)
        deck.add(Card(colour, action="rev"), quantity=2)
        deck.add(Card(colour, action="skip"), quantity=2)

    # add wildcards
    deck.add(Card("W"), quantity=4)
    deck.add(Card("W", action="+4"), quantity=4)

    # shuffle the deck
    if shuffle:
        deck.shuffle()

    return deck


def setup_group():
    """
    Initialises the players in order
    :return: The group of players in the match
    :rtype: Group
    """

    while True:
        try:
            num_players = int(input("How many players are there?\t"))
            break
        except ValueError:
            print("That's not a number, try again")
    group = Group()
    for i in range(num_players):
        name = input(f"What is the name of player {i + 1}?\t")
        group.add(Player(name))

    return group


def setup_game(group):
    """
    Initialise the deck, discard pile, player's hands and state of the game
    :param group: The group of players in the match
    :type group: Group
    :return: The shuffled deck, the game state and whether in game
    :rtype: tuple[Deck, State, bool]
    """

    deck = setup_deck()
    deck.deal(group)  # add group to function inputs and docstring
    state = State()
    in_game = True

    return deck, state, in_game


def initial_card(deck, state):
    """
    Determine the initial card for the game and update the state accordingly
    :param deck: The deck to take the card from
    :type deck: Deck
    :param state: The current game state
    :type state: State
    :return: The initial card, the discard pile and the game state
    :rtype: tuple[Card, Pile]
    """

    current_card = deck.draw()
    while current_card == Card("W", action="+4"):
        deck.add(current_card)
        deck.shuffle()
        current_card = deck.draw()
    discard_pile = Pile(current_card)
    state.update(current_card)
    print(f"The starting card is: {current_card.name}")

    return current_card, discard_pile


def turn_0(current_card, group, state):
    """
    Determines the initial order of play, then gives the appropriate player wild-card colour choice if necessary
    :param current_card: The current card on the discard pile
    :type current_card: Card
    :param group: The group of players in the match
    :type group: Group
    :param state: The current game state
    :type state: State
    """

    group.initial(state)
    if state.turn_order == -1:
        print("The play order is reversed!")
    if current_card == Card("W"):
        print(f"The starting card is a wild card! {group.current_player.name}, this is your hand:")
        group.current_player.display_hand()
        current_card.wild_colour(group.current_player)


def turn(group, deck, discard_pile):
    """
    Performs a single player's turn, allowing a player to draw a card or play an appropriate one
    :param group: The group of players in the match
    :type group: Group
    :param deck: The deck to draw cards from
    :type deck: Deck
    :param discard_pile: The discard pile cards are played onto
    :type discard_pile: Pile
    :return: The card played, if any
    :rtype: Card
    """

    turn_finished = False
    played_card = None

    print(f"It's your turn {group.current_player.name}!")
    input("Press 'enter' when you're ready to do your turn")
    print(f"The current card is: {discard_pile.top.name}")

    for player in group.players:
        if player is not group.current_player and player.hand.size == 1:
            print(f"{player.name} is at UNO!")

    # if none playable draw a card, then offer to play it if possible
    if not group.current_player.playable_hand(discard_pile):
        group.current_player.display_hand()
        print("You have no playable cards, you must draw a card")
        played_card = group.current_player.draw_and_offer(deck, discard_pile)
        turn_finished = True

    # while no card has been played or drawn choose whether to draw or play a card until a card has been played or drawn
    while not turn_finished:
        group.current_player.display_hand()
        while True:
            try:
                card_number = int(input("Choose a card by number in your hand, or 0 to draw instead\t"))
                break
            except ValueError:
                print("That's not a number, try again")

        # choose to not play a card and instead draw, then offer to play it if possible
        if card_number == 0:
            played_card = group.current_player.draw_and_offer(deck, discard_pile)
            turn_finished = True

        # choose a card to play
        elif card_number <= group.current_player.hand.size:
            chosen_card = group.current_player.hand.cards[card_number - 1]
            if not group.current_player.playable_card(chosen_card, discard_pile):
                print("Chosen card isn't playable, choose another!")
            else:
                group.current_player.play(chosen_card, discard_pile)
                played_card = chosen_card
                turn_finished = True

        else:
            print("You don't have that many cards in your hand, try again!")
            print(f"The current card is: {discard_pile.top.name}")

    turn_finished_confirmation(group)

    return played_card


def turn_finished_confirmation(group):
    """
    Confirm with the current player that they are finished with their turn
    :param group: The group playing the match
    :type group: Group
    """

    input(f"Your turn is done {group.current_player.name}, press 'enter' when you're finished")
    print("\n"*25)


def game(group, deck, discard_pile, state):
    """
    Runs a game until a player's hand is empty
    :param group: The group of players in the match
    :type group: Group
    :param deck: The deck used for the game
    :type deck: Deck
    :param discard_pile: The discard pile for the game
    :type discard_pile: Pile
    :param state: The game state at the start of the game
    :type state: State
    :return: Whether still in game or not
    :rtype: bool
    """

    # current player draws any cards if necessary, then skips go if necessary, otherwise do their go as normal
    if state.skip == 1:

        # draw cards if necessary
        if state.forced_draw > 0:
            print(f"Sorry {group.current_player.name}, you must draw {state.forced_draw} cards and skip your go!")
            group.current_player.draw(state.forced_draw, deck)
            print(f"After drawing {state.forced_draw} cards your hand is now:")
            group.current_player.display_hand()
            turn_finished_confirmation(group)
        else:
            print(f"Sorry {group.current_player.name}, your go has been skipped!")
            turn_finished_confirmation(group)

        # move to next player and remove need to skip or draw
        group.next(state)
        state.neutralise()

    # if player's go is not skipped proceed as normal, checking also to see if that player has won
    else:
        played_card = turn(group, deck, discard_pile)

        # if the player has won give them points
        if group.current_player.hand.size == 0:

            # if last played card was a forced draw, first draw the next player those cards
            if state.forced_draw > 0:
                group.players[(group.player_number + state.turn_order) % group.size].draw(state.forced_draw, deck)

            # then determine and increase point totals, and rotate play order so winner goes first next round
            group.give_points()
            group.winner_first()
            return False

        # if the player hasn't won carry on as normal
        else:
            if played_card is not None:
                state.update(played_card)
            group.next(state)

            # if the deck is empty reshuffle it
            if deck.size == 0:
                discard_pile.reset(deck)

    return True


def match(group):
    """
    Play games a points winner to win the match has been found
    :param group: The group of players in the match
    :type group: Group
    :return: Whether still in match or not
    :rtype: bool
    """

    deck, state, in_game = setup_game(group)
    current_card, discard_pile = initial_card(deck, state)
    turn_0(current_card, group, state)

    while in_game:
        in_game = game(group, deck, discard_pile, state)

    # display the current standings
    standings = group.standings
    name_length = max(len(player.name) for player in group.players) + 5
    for position, player in enumerate(standings):
        print(f"{position+1}: {player.name.ljust(name_length)}{player.points}")

    # if a player has reached the score threshold then they win the match
    winning_player = standings[0]
    if winning_player.points >= 500:
        print(f"\nCongratulations {winning_player.name}!!! You've won the match!!!")
        return False

    return True


def main():

    group = setup_group()
    in_match = True

    while in_match:
        in_match = match(group)


main()
