rm -f ~/job.sh.*
qsub -l vlong -l vf=64G job.sh
