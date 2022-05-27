async def first_count_points(cards):
    points = 0

    for card in cards:

        if card[:-2].isdigit():
            points += int(card[:-2])

        elif card[:-2] == "A":
            points += 11

        else:
            points += 10

    return points


async def hit_count_points(points, card):

    if card[:-2].isdigit():
        points += int(card[:-2])

    elif card[:-2] == "A":

        if (points + 11) > 21:
            points += 1
        else:
            points += 11

    else:
        points += 10

    return points


async def player_hit(p_points: int, p_cards: str, next_cards: str):
    next_card = next_cards[:next_cards.find("_")]

    if next_card[:-2].isdigit():
        p_points += int(next_card[:-2])

    elif next_card[:-2] == "A":

        if (p_points + 11) > 21:
            p_points += 1
        else:
            p_points += 11

    else:
        p_points += 10

    p_cards += f"_{next_card}"
    next_cards = next_cards[next_cards.find("_")+1:]

    return [p_points, p_cards, next_cards]
