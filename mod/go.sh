rm -f ~/job.sh.*
qsub -l short -l vf=64G job.sh
