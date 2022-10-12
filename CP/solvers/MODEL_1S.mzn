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

array[1..n] of int : ordered_c = sort_by(1..n, [-heights[c]*widths[c] | c in 1..n]);
 
constraint cumulative(positions_y, heights, widths, w);
constraint cumulative(positions_x, widths, heights, h);
constraint max(i in 1..n)(positions_x[i] + widths[i])<= w;
constraint max(i in 1..n)(positions_y[i] + heights[i])<= h;
constraint diffn_nonstrict(positions_x, positions_y, widths, heights);

% ==== Symmetry breaking constraints ====

% Dominance constraint, adjacent circuits are always better
constraint 
  forall(c in 1..n)(
    member([0] ++ [positions_x[o] + widths[o] | o in 1..n where o != c], positions_x[c]) /\
    member([0] ++ [positions_y[o] + heights[o] | o in 1..n where o != c], positions_y[c])
  );

% The biggest circuit is always placed under and on the left wrt the second biggest
constraint symmetry_breaking_constraint(
  let {
    int: c1 = ordered_c[1], int: c2 = ordered_c[2]
  } in lex_less([positions_y[c1],positions_x[c1]], [positions_y[c2],positions_x[c2]])
);

constraint symmetry_breaking_constraint(
    lex_lesseq(
        [positions_x[i] | i in 1..n],
        [w - positions_x[i] - widths[i]| i in 1..n]
    )
);

solve :: seq_search([
    int_search(positions_y, first_fail, indomain_min),
    int_search(positions_x, first_fail, indomain_min),
    int_search([h], smallest, indomain_min)])
    minimize h;


