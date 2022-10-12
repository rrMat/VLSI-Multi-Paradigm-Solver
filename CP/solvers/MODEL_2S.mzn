include "globals.mzn";
include "diffn.mzn";

int: w;
int: n;
int: h;
array[1..n] of int: widths;
array[1..n] of int: heights;

array[1..n] of var 0..w - min(widths): positions_x; 
array[1..n] of var 0..h - min(heights): positions_y;

array[1..n] of int : ordered_c = sort_by(1..n, [-heights[c]*widths[c] | c in 1..n]);
 
constraint cumulative(positions_y, heights, widths, w);
constraint cumulative(positions_x, widths, heights, h);
constraint max(i in 1..n)(positions_x[i] + widths[i])<= w;
constraint max(i in 1..n)(positions_y[i] + heights[i])<= h;
constraint diffn_nonstrict(positions_x, positions_y, widths, heights);

% ==== Symmetry breaking constraints ====


constraint symmetry_breaking_constraint(
    lex_lesseq(
        [positions_x[i] | i in 1..n],
        [w - positions_x[i] - widths[i]| i in 1..n]
    )
);

constraint symmetry_breaking_constraint(
    lex_lesseq(
        [positions_y[i] | i in 1..n],
        [h - positions_y[i] - heights[i] |i in 1..n]
    )
);

solve :: seq_search([
    int_search(positions_y, first_fail, indomain_min),
    int_search(positions_x, first_fail, indomain_min),
    ])
    satisfy;


