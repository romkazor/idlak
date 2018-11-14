#!/bin/bash
set -euo pipefail

durcmpdir=$1
datadir=$2

(echo '#!MLF!#'; for cmp in $durcmpdir/*.cmp; do
    cat $cmp | awk -v nstate=5 -v id=`basename $cmp .cmp` '
function ceil(val) {
  return (val == int(val)) ? val : int(val)+1
}
BEGIN{print "\"" id ".lab\""; tstart = 0 }
{
  pd += $2;
  sd[NR % nstate] = $1}
(NR % nstate == 0) {
  mpd = pd / nstate;
  smpd = 0;
  for (i = 1; i <= nstate; i++)
    smpd += sd[i % nstate];
  rmpd = ceil((smpd + mpd) / 2);
  for (i = 1; i <= nstate; i++)
    sd[i % nstate] = ceil(sd[i % nstate] / smpd * rmpd);
  if (sd[0] <= 0)
    sd[0] = 1;
  if (sd[nstate-1] <= 0)
      sd[nstate-1] = 1;
  for (i = 1; i <= nstate; i++) {
    if (sd[i % nstate] > 0) {
      tend = tstart + sd[i % nstate] * 50000;
      print tstart, tend, int(NR / nstate), i-1;
      tstart = tend;
    }
  }
  pd = 0;
}
END{print "."}'
done) > $datadir/synth_lab.mlf
