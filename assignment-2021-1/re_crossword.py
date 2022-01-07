import csv
import re
import sre_yield
import string
from collections import deque
import sys


def find_longest_and_shortest_words(words):
    max_w, min_w = 0, 25
    for value in words.values():
        max_w = value['length'] if max_w < value['length'] else max_w
        min_w = value['length'] if min_w > value['length'] else min_w
    return max_w, min_w


def extract_graph_from_csv(path):
    graph, words_info = {}, {}
    with open(path, newline='') as csv_file:
        words = csv.reader(csv_file, delimiter=',')
        for row in words:
            nodes = [int(i) for i in row[0:-1:2]]  # keep node and its neighbors
            intersect = [int(i) for i in row[3::2]]  # keep intersections of nodes
            length_of_word = len(row[1])  # the length of dots

            if nodes[0] not in graph:
                graph[nodes[0]] = {'all': {}, 'next_node': None}
                words_info[nodes[0]] = {}

            for index, neighbor in enumerate(nodes[1:]):
                graph[nodes[0]]['all'].update({neighbor: intersect[index]})

            words_info[nodes[0]].update({'length': length_of_word, 'word': row[1],
                                         'unfilled_word': row[1], 'regex': None})
        longest, shortest = find_longest_and_shortest_words(words_info)

    return graph, words_info, longest, shortest


def read_txt(path):
    expressions = {}
    with open(path, 'r') as txt_file:
        for row in txt_file:
            # store expressions to a dictionary
            expressions.update({row.strip(): {'all': [], 'used': False}})
    return expressions


def generate_yields(regex, longest, shortest):
    yields = [sre_yield.AllStrings(expression, max_count=5, charset=string.ascii_uppercase) for expression in regex]
    for i, key in enumerate(regex):
        for j in yields[i]:
            if shortest <= len(j) <= longest and j not in regex[key]['all']:
                regex[key]['all'].append(j)
    return regex


def calculate_known_words_metric(key, info):
    known = re.subn(r'\w', '', info[key]['word'])[1]  # known characters
    known = 1 if known == 0 else known
    info[key].update({'known': info[key]['length'] / known})


def find_first_crossword(info):
    best, which = 20.0, 0
    for key in info:
        calculate_known_words_metric(key, info)
        if (info[key]['known']) < best:  # check if best has more unknown characters
            best = info[key]['known']
            which = key
    return which


def update_known_chars(node, graph, info):
    for value in graph[node]['all']:
        info[value]['word'] = \
            info[value]['word'][:graph[node]['all'][value]] + \
            info[node]['word'][graph[value]['all'][node]] + \
            info[value]['word'][graph[node]['all'][value] + 1:]
        calculate_known_words_metric(value, info)


def set_path_bfs(node, graph, stack):
    q = deque()
    visited, inqueue = [False] * len(graph), [False] * len(graph)
    q.appendleft(node)
    inqueue[node] = True

    while not (len(q) == 0):
        c = q.pop()
        stack.append(c)
        inqueue[c], visited[c] = False, True
        for k in graph[c]['all']:
            graph[k]['all'].update({c: graph[k]['all'][c]})
            if not visited[k] and not inqueue[k]:
                q.appendleft(k)
                inqueue[k] = True


def save_unfilled_word(node, graph, info, path):
    for neighbor in graph[node]['all']:
        if path.index(neighbor) > path.index(node):
            info[neighbor]['unfilled_word'] = info[neighbor]['word']


def backtrack(graph, info, node, all_yields, path):
    pattern, counter = re.compile(r'\w'), 0
    match_length = len([*re.finditer(pattern, info[node]['word'])])  # the length of known characters
    g = [m for m in pattern.finditer(info[node]['word'])]
    true_yields = [key for key in all_yields if not all_yields[key]['used']]
    for key in true_yields:
        untested_yields = [y for y in all_yields[key]['all'] if len(y) == info[node]['length']]
        for y in untested_yields:
            for m in g:
                if info[node]['word'][m.start()] == y[m.start()]:
                    counter += 1

            if counter == match_length:
                fill, regex = y, key
                info[node]['word'] = fill  # write the word
                info[node]['regex'] = regex  # write the expression
                all_yields[regex]['used'] = True

                calculate_known_words_metric(node, info)
                update_known_chars(node, graph, info)  # write changes to intersections

                save_unfilled_word(node, graph, info, path)
                if graph[node]['next_node'] is None: return True
                if backtrack(graph, info, graph[node]['next_node'], all_yields, path): return True

                info[node]['word'] = info[node]['unfilled_word']
                info[node]['regex'] = None
                all_yields[regex]['used'] = False
                calculate_known_words_metric(node, info)
                update_known_chars(node, graph, info)

            counter = 0
    return False


def main():
    csv_file, txt_file, graph_path = str(sys.argv[1]), str(sys.argv[2]), []
    graph, info, longest, shortest = extract_graph_from_csv(csv_file)
    all_yields = generate_yields(read_txt(txt_file), longest, shortest)

    start = find_first_crossword(info)
    set_path_bfs(start, graph, graph_path)

    for index, n in enumerate(graph_path[:-1]):  # set the exact previous visited node, in order to backtrack
        graph[n]['next_node'] = graph_path[index+1]

    backtrack(graph, info, start, all_yields, graph_path)

    for i in range(len(info)):
        print(i, info[i]['regex'], info[i]['word'])


if __name__ == '__main__':
    main()
