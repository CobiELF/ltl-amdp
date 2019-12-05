if __name__ == "__main__":
    # create test tsvs
    for file_number in range(1,6):
        fp_train_src = open("TRAIN_" + str(file_number) + "_SRC", 'r')
        fp_train_tar = open("TRAIN_" + str(file_number) + "_TAR", 'r')
        fp_test_src = open("TEST_" + str(file_number) + "_SRC", 'r')
        fp_test_tar = open("TEST_" + str(file_number) + "_TAR", 'r')

        fp_train_tsv = open("TRAIN_" + str(file_number) + ".tsv", 'w')
        fp_test_tsv = open("TEST_" + str(file_number) + ".tsv", 'w')
        for line in fp_train_src:
            fp_train_tsv.write(line[:-1] + "\t" + fp_train_tar.readline())
            fp_test_tsv.write(fp_test_src.readline()[:-1] + "\t" + fp_test_tar.readline())

        fp_train_src.close()
        fp_train_tar.close()
        fp_test_src.close()
        fp_test_tar.close()
        fp_train_tsv.close()
        fp_test_tsv.close()