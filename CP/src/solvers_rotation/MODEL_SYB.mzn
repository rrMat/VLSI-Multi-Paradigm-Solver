include "globals.mzn";
include "diffn.mzn";

int: w;
int: n;
array[1..n] of int: widths;
array[1..n] of int: heights;

int: max_h = sum(heights);  
int: sum_of_widths = sum(widths);
int: min_h_ratio = (sum(i in 1..n)(widths[i] * heights[i])) div w; 
int: min_h = if sum_of_widths <= w then max(heights) else min_h_ratio endif;

var min_h..max_h: h;  
array[1..n] of var 0..w - min(widths): X; 
array[1..n] of var 0..max_h - min(heights): Y;

array[1..n] of var bool: rotations;
array[1..n] of var int: actual_widths = [(widths[i]*(1-rotations[i]) + (heights[i])*rotations[i]) | i in 1..n];
array[1..n] of var int: actual_heights = [(widths[i]*rotations[i]) + (heights[i]*(1-rotations[i])) | i in 1..n];
 

constraint max(i in 1..n)(Y[i] + actual_heights[i]) <= h;
constraint max(i in 1..n)(X[i] + actual_widths[i]) <= w; 
constraint diffn_nonstrict(X, Y, actual_widths, actual_heights);
constraint cumulative(Y, actual_heights, actual_widths, w);
constraint cumulative(X, actual_widths, actual_heights, h);

% ==== Symmetry breaking constraints ====

constraint symmetry_breaking_constraint(
    lex_lesseq(
        [X[i] | i in 1..n],
        [w - X[i] - actual_widths[i]| i in 1..n]
    )
);

constraint symmetry_breaking_constraint(
    lex_lesseq(
        [Y[i] | i in 1..n],
        [h - Y[i] - actual_heights[i] |i in 1..n]
    )
);

solve :: seq_search([
    int_search(Y, first_fail, indomain_min),
    int_search(X, first_fail, indomain_min),
    int_search(rotations, first_fail, indomain_min),
    int_search([h], smallest, indomain_min)])
    minimize h;


