include "globals.mzn";
include "diffn.mzn";

int: w;
int: n;
array[1..n] of int: widths;
array[1..n] of int: heights;

int: sum_of_widths = sum(widths);
int: min_h_ratio = (sum(i in 1..n)(widths[i] * heights[i])) div w; 
int: min_h = if sum_of_widths <= w then max(heights) else min_h_ratio endif;
int: max_h = if sum_of_widths <= w then max(heights) else sum(heights) endif;

var min_h..max_h: h;  
array[1..n] of var 0..w - min(widths): X; 
array[1..n] of var 0..max_h - min(heights): Y;

constraint max(i in 1..n)(Y[i] + heights[i]) <= h;
constraint max(i in 1..n)(X[i] + widths[i]) <= w; 
constraint diffn_nonstrict(X, Y, widths, heights);
constraint cumulative(Y, heights, widths, w);
constraint cumulative(X, widths, heights, h);

% ==== Symmetry breaking constraints ====

constraint symmetry_breaking_constraint(
    lex_lesseq(
        [X[i] | i in 1..n],
        [w - X[i] - widths[i]| i in 1..n]
    )
);

constraint symmetry_breaking_constraint(
    lex_lesseq(
        [Y[i] | i in 1..n],
        [h - Y[i] - heights[i]| i in 1..n]
    )
);


solve :: seq_search([
    int_search(Y, first_fail, indomain_min),
    int_search(X, first_fail, indomain_min),
    int_search([h], smallest, indomain_min)])
    minimize h;
    



