if __name__ == "__main__":
    # create test tsvs
    for file_number in range(1,6):
        fp_src = open("mod/TEST_" + str(file_number) + "_SRC", 'r')
        fp_tar = open("mod/TEST_" + str(file_number) + "_TAR", 'r')
        fp_tsv = open("mod/TEST_" + str(file_number) + ".tsv", 'w')

        for line in fp_src:
            fp_tsv.write(line[:-1] + "\t" + fp_tar.readline())

        fp_src.close()
        fp_tar.close()
        fp_tsv.close()

    for holdout in range(1,6):
        print(holdout)
        fp_train = open("mod/TRAIN_" + str(holdout) + ".tsv", 'w')
        for test_num in range(1, holdout):
            fp_test = open("mod/TEST_" + str(file_number) + ".tsv", 'r')
            for line in fp_test:
                fp_train.write(line)
            fp_test.close()
        for test_num in range(holdout+1, 6):
            fp_test = open("mod/TEST_" + str(file_number) + ".tsv", 'r')
            for line in fp_test:
                fp_train.write(line)
            fp_test.close()
        fp_train.close()
        