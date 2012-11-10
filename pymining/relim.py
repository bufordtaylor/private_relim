from collections import defaultdict, deque, OrderedDict, namedtuple
from pprint import pprint


__all__ = ('relim2', 'get_relim_input2', 'clean_data')

# Normally you wouldn't be declaring a global variable
# I set an __all__ for the sake of keeping it clean
# I'm using a namedtuple here for speed, assuming this will be handling
# massive datasets, as it beats objects in speed tests
# (although using slots would be fast too)
Relim = namedtuple('Relim', 'relim_input key_map')

def clean_data(raw_data):
    """takes raw data from file and makes a list of artist lists

        raw_data example:
            'Radiohead,Morrissey,Limp Bizkit\nBlur,Tool\n'
    """
    lines = [line for line in art_string.split('\n')]
    return [a for a in [line.split(',') for line in lines]]

def count_artist_frequency(user_artists):
    """returns:
    (list of tuples of frequency & artist set, dict of artist frequencies)

        Example input:
        (
            ('Radiohead', 'Morrissey', 'Delays',),
            ('Band of Horses', 'Radiohead', 'Morrissey')
        )


        Example output:
        ([
            (
                (1, 'Band of Horses'),
                (2, 'Morrissey'),
                (2, 'Radiohead')
            ),
            (
                (1, 'Delays'),
                (2, 'Morrissey'),
                (2, 'Radiohead')
            )
         ],
         defaultdict(<type 'int'>, {
             'Morrissey': 2,
             'Delays': 1,
             'Band of Horses': 1,
             'Radiohead': 2
             })
        )
    """
    artist_collection = []

    # make a dictionary of {artist: frequency}
    # O(n^2)
    frequencies = defaultdict(int)
    for artists in user_artists:
        for artist in artists:
            frequencies[artist] += 1

    # second pass to make a collection of artists with associated frequencies
    # O(n^2)
    for artists in user_artists:
        # Sort each artist list (infrequent key first)
        l = [(frequencies[artist], artist) for artist in artists]
        l.sort()
        artist_collection.append(tuple(l))

    # Sort all user_artists. Those with infrequent key first, first
    artist_collection.sort()

    return (artist_collection, frequencies)

def _new_relim_input(size, key_map):
    i = 0
    l = []
    for key in key_map:
        if i >= size:
            break
        l.append(((0, key), []))
        i = i + 1
    return l


def _get_key_map(frequencies):
    print '...'
    print '...'
    print 'frequencies', frequencies
    l = [(frequencies[k], k) for k in frequencies]
    print '...'
    print 'l', l
    l.sort(reverse=True)
    key_map = OrderedDict()
    for i, v in enumerate(l):
        key_map[v] = i
    print '......'
    print key_map
    return key_map

def get_relim_input2(transactions):
    '''Given a list of transactions and a key function, returns a data
       structure used as the input of the relim algorithm.

       :param transactions: a sequence of sequences. [ [transaction items...]]
       :param key_func: a function that returns a comparable key for a
        transaction item.
    '''

    # Data Structure
    # relim_input[x][0] = (count, key_freq)
    # relim_input[x][1] = [(count, (key_freq, )]
    #
    # in other words:
    # relim_input[x][0][0] = count of trans with prefix key_freq
    # relim_input[x][0][1] = prefix key_freq
    # relim_input[x][1] = lists of transaction rests
    # relim_input[x][1][x][0] = number of times a rest of transaction appears
    # relim_input[x][1][x][1] = rest of transaction prefixed by key_freq

    (asorted_seqs, frequencies) = count_artist_frequency(transactions)
    print
    pprint((asorted_seqs, frequencies))
    key_map = _get_key_map(frequencies)

    relim_input = _new_relim_input(len(key_map), key_map)
    print 'key_map', key_map
    print '................'
    print 'relim_input', relim_input
    for seq in asorted_seqs:
        if not seq:
            continue
        index = key_map[seq[0]]
        ((count, char), lists) = relim_input[index]
        rest = seq[1:]
        found = False
        for i, (rest_count, rest_seq) in enumerate(lists):
            if rest_seq == rest:
                lists[i] = (rest_count + 1, rest_seq)
                found = True
                break
        if not found:
            lists.append((1, rest))
        relim_input[index] = ((count + 1, char), lists)
        print '......', index
        print relim_input[index]
    return Relim(relim_input, key_map)


def relim2(rinput, min_support=2):
    '''Finds frequent item sets of items appearing in a list of transactions
       based on Recursive Elimination algorithm by Christian Borgelt.

       In my synthetic tests, Relim outperforms other algorithms by a large
       margin. This is unexpected as FP-Growth is supposed to be superior, but
       this may be due to my implementation of these algorithms.

       :param rinput: The input of the algorithm. Must come from
        `get_relim_input`.
       :param min_support: The minimal support of a set to be included.
       :rtype: A set containing the frequent item sets and their support.
    '''
    fis = set()
    report = {}
    _relim2(rinput, fis, report, min_support)
    return report

    # Data Structure
    # relim_input[x][0] = (count, key_freq)
    # relim_input[x][1] = [(count, (key_freq, )]
    #
    # in other words:
    # relim_input[x][0][0] = count of trans with prefix key_freq
    # relim_input[x][0][1] = prefix key_freq
    # relim_input[x][1] = lists of transaction rests
    # relim_input[x][1][x][0] = number of times a rest of transaction appears
    # relim_input[x][1][x][1] = rest of transaction prefixed by key_freq
def _relim2(rinput, fis, report, min_support):
    # Maybe this one isn't necessary
    while len(rinput.relim_input) > 0:
        item = rinput.relim_input[-1][0][1]
        s = rinput.relim_input[-1][0][0]
        if s >= min_support:
            fis.add(item[1])
            #print('Report {0} with support {1}'.format(fis, s))
            report[tuple(fis)] = s
            b = _new_relim_input(len(rinput.relim_input) - 1, rinput.key_map)
            rest_lists = rinput.relim_input[-1][1]

            for (count, rest) in rest_lists:
                if not rest:
                    continue
                k = rest[0]
                index = rinput.key_map[k]
                new_rest = rest[1:]
                # Only add this rest if it's not empty!
                ((k_count, k), lists) = b[index]
                if len(new_rest) > 0:
                    lists.append((count, new_rest))
                b[index] = ((k_count + count, k), lists)
            _relim2(Relim(b, rinput.key_map), fis, report, min_support)
            fis.remove(item[1])

        rest_lists = rinput.relim_input[-1][1]
        for (count, rest) in rest_lists:
            if not rest:
                continue
            k = rest[0]
            index = rinput.key_map[k]
            new_rest = rest[1:]
            ((k_count, k), lists) = rinput.relim_input[index]
            if len(new_rest) > 0:
                lists.append((count, new_rest))
            rinput.relim_input[index] = ((k_count + count, k), lists)
        rinput.relim_input.pop()

art_string = "Radiohead,Pulp,Morrissey,Delays,Stereophonics,Blur,Suede,Sleeper,The La's,Super Furry Animals\n Band of Horses,Iggy Pop,The Velvet Underground,Radiohead,The Decemberists,Morrissey,Television\nPulp,Blur,Sleeper,Tool\nRadiohead,Morrissey,Limp Bizkit\nBlur,Tool\n"

artists = clean_data(art_string)

reliminput = get_relim_input2(artists)
#pprint(reliminput)
print
pprint(relim2(reliminput))
