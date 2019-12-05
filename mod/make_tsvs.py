if __name__ == "__main__":
    # create test tsvs
    for file_number in range(1,6):
        #training dataset
        fp_train_src = open("TRAIN_" + str(file_number) + "_SRC", 'r')
        fp_train_tar = open("TRAIN_" + str(file_number) + "_TAR", 'r')
        fp_train_tsv = open("TRAIN_" + str(file_number) + ".tsv", 'w')

        src_lines = fp_train_src.readlines()
        tar_lines = fp_train_tar.readlines()
        for i in range(len(src_lines)):
            fp_train_tsv.write(src_lines[i][:-1] + "\t" + tar_lines[i])

        fp_train_src.close()
        fp_train_tar.close()
        fp_train_tsv.close()

        # test dataset

        fp_test_src = open("TEST_" + str(file_number) + "_SRC", 'r')
        fp_test_tar = open("TEST_" + str(file_number) + "_TAR", 'r')
        fp_test_tsv = open("TEST_" + str(file_number) + ".tsv", 'w')

        src_lines = fp_test_src.readlines()
        tar_lines = fp_test_tar.readlines()
        for i in range(len(src_lines)):
            fp_test_tsv.write(src_lines[i][:-1] + "\t" + tar_lines[i])

        fp_test_src.close()
        fp_test_tar.close()
        fp_test_tsv.close()