import itertools as it
import argparse


def read_txt(path):
    with open(path, 'r') as txt_file:
        points = [(int(line.split()[0]), int(line.split()[1])) for line in txt_file.readlines()]
    return points


def calculate_slope(pair):
    if pair[0][0] == pair[1][0]:  # If line is vertical, slope is Undefined (None)
        return None
    if pair[0][1] == pair[1][1]:  # If line is horizontal, slope is 0
        return 0

    return (pair[0][1] - pair[1][1]) / (pair[0][0] - pair[1][0])


def remove_unnecessary_lines(all_lines):
    c = 0
    for small_line in all_lines.copy():
        i = len(all_lines) - 1
        while len(small_line) < len(all_lines[i]):
            if set(small_line).issubset(all_lines[i]):
                c += 1
                all_lines.remove(small_line)
                break
            i -= 1

    return all_lines


def find_lines(all_lines, two_pl, points, method=False):
    if method:
        all_lines.clear()
    multiple_pl = dict.fromkeys(points)
    for p in points:
        multiple_pl.update({p: {}})
        for comb in two_pl:
            if comb[0] == p:
                slope = calculate_slope(comb)
                if method:
                    if not slope:
                        if slope in multiple_pl[p]:
                            multiple_pl[p][slope].append(comb[1])
                        else:
                            multiple_pl[p].update({slope: []})
                            multiple_pl[p][slope].append(comb[1])
                else:
                    if slope in multiple_pl[p]:
                        multiple_pl[p][slope].append(comb[1])

                    else:
                        multiple_pl[p].update({slope: []})
                        multiple_pl[p][slope].append(comb[1])

        for value in multiple_pl[p].values():
            # for example: [(2,2), (3,3)] is unnecessary when we already have [(1,1), (2,2), (3,3)]
            to_remove = [list(i) for i in it.combinations(value, 2)]
            for c in to_remove:
                two_pl.remove(c)

        for value in multiple_pl[p].values():
            combination = [p] + value  # insert tuple in list and join with the rest of the points
            all_lines.extend([combination])

    for key, value in sorted(multiple_pl.items(), reverse=True):
        if value:
            for i in value.values():
                [multiple_pl.pop(h) for h in i if h in multiple_pl]

    for key, value in multiple_pl.items():
        if not value:
            neighbor = (key[0]+1, key[1])
            all_lines.extend([(key, neighbor)])
            points.append(neighbor)

    all_lines = remove_unnecessary_lines(all_lines)
    return all_lines, points


def find_covering_points(subset, points_to_cover=None, method=False):
    if not method:
        return sum(point in points_to_cover for point in subset)
    else:
        covering_points = set(it.chain(*subset))
        return len(points_to_cover) if sorted(list(covering_points)) == sorted(points_to_cover) else 0


def find_optimal_lines(all_lines, points_to_cover, method=False):
    all_lines.sort(key=lambda x: len(x), reverse=True)
    if method:
        for i in range(0, len(points_to_cover)):
            subset = it.combinations(all_lines, i)
            try:
                subset = next(filter(lambda x:
                                     find_covering_points(x, points_to_cover, method) == len(points_to_cover), subset))
            except StopIteration:
                continue
            if subset:
                return subset
            else:
                continue
    else:
        solution = []
        while points_to_cover:
            next_best_line = all_lines[0]
            covers_more = find_covering_points(all_lines[0], points_to_cover, method)
            for current_line in all_lines[1:]:
                if find_covering_points(current_line, points_to_cover, method) > covers_more:
                    next_best_line = current_line
                    covers_more = find_covering_points(current_line, points_to_cover, method)

            solution.append(next_best_line)

            for p in next_best_line:
                points_to_cover.remove(p) if p in points_to_cover else True
            all_lines.remove(next_best_line)
        return solution


def beautiful_print(result):
    result = list(result)
    for index, l in enumerate(result):
        result[index] = sorted(l, key=lambda x: x,)  # sort points of lines based on points' order
    result = sorted(result, key=lambda x: x[0],)  # sort lines of list based on first point of each line
    result = sorted(result, key=lambda x: len(x), reverse=True)  # sort lines of list based on length of lines

    for line in result:
        print(*line)


def main():
    parser = argparse.ArgumentParser(
        description='Find the fewest lines that cover all points on a Cartesian coordinate system.',
        epilog='This is a set covering problem.')

    parser.add_argument('-f', action='store_true', default=False,
                        help='Find optimal combination of lines. If omitted, greedy algorithm will be used.')
    parser.add_argument('-g', action='store_true', default=False,
                        help='Only lines parallel to horizontal and vertical axes will be used.')
    parser.add_argument('points_file',
                        help='the file from which the points will be read')
    args = parser.parse_args()

    points = read_txt(args.points_file)
    two_points_line = [list(combination) for combination in it.combinations(points, 2)]  # lines with 2 points
    all_lines = two_points_line.copy()
    all_lines, points = find_lines(all_lines, two_points_line, points, args.g)
    all_lines = find_optimal_lines(all_lines, points, args.f)

    beautiful_print(all_lines)


if __name__ == "__main__":
    main()
