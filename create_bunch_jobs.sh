#!/bin/bash
# Expand the template into multiple files, one for each item to be processed.
mkdir ./jobs -p
for i in 4 8 12 16 24 32
do
  cat meta_run_job.yaml | sed "s/\$NLATENTS/$i/" > ./jobs/job-$i.yaml
done