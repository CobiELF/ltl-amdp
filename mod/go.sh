rm -f ~/job.sh.*
qsub -l long -l vf=64G job.sh
