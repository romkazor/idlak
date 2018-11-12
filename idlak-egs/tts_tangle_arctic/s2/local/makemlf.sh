#!/bin/bash
set -euo pipefail

duroutdir=$1
datadir=$2

(echo '#!MLF!#'; for cmp in $duroutdir/cmp/*.cmp; do
    cat $cmp | awk -v nstate=5 -v id=`basename $cmp .cmp` 'BEGIN{print "\"" id ".lab\""; tstart = 0 }
{
  pd += $2;
  sd[NR % nstate] = $1}
(NR % nstate == 0){
   mpd = pd / nstate;
   smpd = 0;
   for (i = 1; i <= nstate; i++) smpd += sd[i % nstate];
   rmpd = int((smpd + mpd) / 2 + 0.5);
   # Normal phones
   if (int(sd[0] + 0.5) == 0) {
      for (i = 1; i <= 3; i++) {
         sd[i % nstate] = int(sd[i % nstate] / smpd * rmpd + 0.5);
      }
      if (sd[3] <= 0) sd[3] = 1;
      for (i = 4; i <= nstate; i++) sd[i % nstate] = 0;
   }
   # Silence phone
   else {
      for (i = 1; i <= nstate; i++) {
          sd[i % nstate] = int(sd[i % nstate] / smpd * rmpd + 0.5);
      }
      if (sd[0] <= 0) sd[0] = 1;
   }
   if (sd[1] <= 0) sd[1] = 1;
   smpd = 0;
   for (i = 1; i <= nstate; i++) smpd += sd[i % nstate];
   for (i = 1; i <= nstate; i++) {
        if (sd[i % nstate] > 0) {
           tend = tstart + sd[i % nstate] * 50000;
           print tstart, tend, int(NR / nstate), i-1;
           tstart = tend;
        }
   }
   pd = 0;
}'
done) > $datadir/synth_lab.mlf