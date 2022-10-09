include "globals.mzn";
include "diffn.mzn";

int: w;
int: n;
array[1..n] of int: widths;
array[1..n] of int: heights;

int: max_h = sum(heights);  
int: min_h = (sum(i in 1..n)(widths[i] * heights[i])) div w; 

var min_h..max_h: h;  
array[1..n] of var 0..w - min(widths): positions_x; 
array[1..n] of var 0..max_h - min(heights): positions_y;
 
constraint cumulative(positions_y, heights, widths, w);
%constraint cumulative(positions_x, widths, heights, h);
constraint max(i in 1..n)(positions_x[i] + widths[i])<= w;
constraint max(i in 1..n)(positions_y[i] + heights[i])<= h;
constraint diffn_nonstrict(positions_x, positions_y, widths, heights);

solve :: seq_search([
    int_search(positions_y, first_fail, indomain_min),
    int_search(positions_x, first_fail, indomain_min),
    int_search([h], smallest, indomain_min)])
    minimize h;


