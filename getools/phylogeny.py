import json
import numpy as np

def print_dist_matrix(mat,labels):
    print(' '.join(labels))
    mat_list = mat.tolist()
    for mat_row in mat_list:

        mat_line_str =  ' '.join([str(x) for x in mat_row])
        print(mat_line_str)


def num_snps(parsed_data_line):
    n_snps = 0
    for data_entry in parsed_data_line['diffs']:
        if data_entry['type'] == 'SNP':
            n_snps +=1

    return n_snps



def create_dist_matrix(diffs):
    mat = np.zeros((len(diffs),len(diffs)),dtype=int)
    for i,diff_line_1 in enumerate(diffs):
        num_snps_1 = 0
        for diff_entry_1 in diff_line_1['diffs']:
            if diff_entry_1['type'] == 'SNP':
                num_snps_1 += 1
        print('file: ',diff_line_1['file'], ' num snps: ',num_snps_1)
        for j,diff_line_2 in enumerate(diffs):
            if i == j:
                mat[i][j] = 0
            else:
                num_snps_2 = 0
                num_matches = 0
                for diff_entry_2 in diff_line_2['diffs']:
                    if diff_entry_2['type'] == 'SNP':
                        num_snps_2 += 1

                for diff_entry_1 in diff_line_1['diffs']:
                    match = False
                    if diff_entry_1['type'] == 'SNP':
                        for diff_entry_2 in diff_line_2['diffs']:
                            if diff_entry_2['type'] == 'SNP':
                                if (diff_entry_1['pos'] == diff_entry_2['pos']) and (diff_entry_1['other'] == diff_entry_2['other']):
                                    match = True
                                    break
                    if match:
                        num_matches += 1
                num_diffs = num_snps_1 + num_snps_2 - (2 * num_matches)
                mat[i][j] = num_diffs

    return mat


def parse_data_line(line):
    diff_list = line.split('\t')
    diff_line = {'file':diff_list[0],'diffs':json.loads(diff_list[1])}
    return diff_line


if __name__ == '__main__':
    file_name = 'out_diffs.txt'
    with open("../test_data/covid19/" + file_name) as file:  # Use file to refer to the file object
        data = file.read()

    data_lines = data.split('\n')

    diffs = []
    labels = ['ref']

    diffs = [{'file':'ref','diffs':[]}]
    for data in data_lines:
        print('data: ',data)
        if len(data) == 0:
            pass
        else:
            labels.append(data.split('\t')[0])
            parsed_data_line = parse_data_line(data)
            n_snps = num_snps(parsed_data_line)
            diffs.append(parsed_data_line)

    print(diffs)

    diff_to_ref = []



    mat = create_dist_matrix(diffs)

    print_dist_matrix(mat,labels)


