

def levenshtein_similarity(str1, str2):
    # remove all non-alphabetic characters and convert to lowercase
    str1 = ''.join(filter(str.isalpha, str1)).lower()
    str2 = ''.join(filter(str.isalpha, str2)).lower()

    # Create a matrix to hold the distances
    d = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]

    # Initialize the first row and column of the matrix
    for i in range(len(str1) + 1):
        d[i][0] = i
    for j in range(len(str2) + 1):
        d[0][j] = j

    # Fill in the rest of the matrix
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i - 1] == str2[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]) + 1

    # return normalized distance
    return 1 - d[-1][-1] / max(len(str1), len(str2))
