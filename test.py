def calculate_remaining_accessible_wastes(
    n_green_wastes, n_yellow_wastes, n_red_wastes
) -> int:
    unaccessible_total_wastes = 0
    unaccessible_yellow_wastes = n_yellow_wastes % 2

    # If there is one yellow waste unaccessible, it will be accessible if there are two green wastes for it
    if unaccessible_yellow_wastes == 1 and n_green_wastes >= 2:
        unaccessible_yellow_wastes = 0
        n_green_wastes -= 2

    unaccessible_green_wastes = n_green_wastes % 4
    if unaccessible_green_wastes >= 2:
        unaccessible_green_wastes -= 2
        unaccessible_yellow_wastes += 1

    unaccessible_total_wastes += unaccessible_yellow_wastes + unaccessible_green_wastes
    return unaccessible_total_wastes


print("3,2,1 : ", calculate_remaining_accessible_wastes(3, 2, 1))  # 2
print("3,2,2 : ", calculate_remaining_accessible_wastes(3, 2, 2))  # 2
print("4,3,3 : ", calculate_remaining_accessible_wastes(4, 3, 3))  # 1
