param w; # width of the plate
param n; # number of circuits
set I := {1..n};
param widths {1..n}; # widths of the circuits
param heights {1..n}; # heights of the circuits

param h_lb := (sum {i in I} widths[i]*heights[i]) / w; # lower bound for H
param h_ub := sum {i in I} heights[i]; # upper bound for H

# big Ms for max and overlapping constraint
param M_horizontal := w;
param M_vertical := h_ub;

# lower left coordinates of the circuits
var Coordinates_x {i in I} integer >= 0, <= w - widths[i];
var Coordinates_y {i in I} integer >= 0, <= h_ub - heights[i];
# top y coordinates for all the circuits
var Circuit_heights {i in I} =
	Coordinates_y[i] + heights[i];
# binary variables for linear max constraint
var Max {i in I} binary;
# maximum of the Circuit_heights
var Max_height integer >= h_lb, <= h_ub;
# binary variables for linear overlapping constraint 
var Not_overlaps {1..4, i in I, j in I: i < j} binary;

# objective function
minimize H:
	Max_height;
	
# max constraint
subject to Only_one_is_max:
		sum {i in I} Max[i] = 1;

subject to Circuit_i_is_max_1 {i in I}:
	Max_height >= Circuit_heights[i];

subject to Circuit_i_is_max_2 {i in I}:
	Max_height - Circuit_heights[i] <= M_vertical * (1 - Max[i]);

# non overlapping constraints
subject to None_overlapping {i in I, j in I: i < j}:
	sum {d in 1..4} Not_overlaps[d,i,j] >= 1;
	
subject to J_is_right {i in I, j in I: i < j}:
	Coordinates_x[i] + widths[i] - Coordinates_x[j] <= M_horizontal * (1 - Not_overlaps[1,i,j]);

subject to J_is_left {i in I, j in I: i < j}:
	Coordinates_x[j] + widths[j] - Coordinates_x[i] <= M_horizontal * (1 - Not_overlaps[2,i,j]);

subject to J_is_up {i in I, j in I: i < j}:
	Coordinates_y[i] + heights[i] - Coordinates_y[j] <= M_vertical * (1 - Not_overlaps[3,i,j]);
	
subject to J_is_down {i in I, j in I: i < j}:
	Coordinates_y[j] + heights[j] - Coordinates_y[i] <= M_vertical * (1 - Not_overlaps[4,i,j]);

