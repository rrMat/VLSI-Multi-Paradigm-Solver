param w; # width of the plate
param n; # number of chips
set I := {1..n};
param widths {1..n}; # widths of the chips
param heights {1..n}; # heights of the chips

param h_lb := (sum {i in I} widths[i]*heights[i]) / w; # lower bound for H
param h_ub := sum {i in I} heights[i]; # upper bound for H
param x_ub := w - min {i in I}(widths[i]); # upper bound for Coordinates_x
param y_ub := h_ub - min{i in I}(heights[i]); # upper bound for Coordinates_y

# big Ms for max and overlapping constraint
param M_horizontal := w;
param M_vertical := h_ub;

# lower left coordinates of the chips
var Coordinates_x {i in I} integer >= 0, <= x_ub;
var Coordinates_y {i in I} integer >= 0, <= y_ub;
# top y coordinates for all the chips
var Chip_heights {i in I} =
	Coordinates_y[i] + heights[i];
# binary variables for linear max constraint
var Max_i {i in I} binary;
# maximum of the Chip_heights
var Max_height integer >= h_lb, <= h_ub;
# binary variables for linear overlapping constraint 
var Not_overlaps_ind {1..4, i in I, j in I: i < j} binary;

# objective function
minimize H:
	Max_height;
	
# enforcing chips to not go out of the plate horizontally
subject to Total_width {i in I}:
	Coordinates_x[i] + widths[i] <= w;
	
# max constraint
subject to Only_one_is_max:
		sum {i in I} Max_i[i] = 1;

subject to Chip_i_is_max_1 {i in I}:
	Max_height >= Chip_heights[i];

subject to Chip_i_is_max_2 {i in I}:
	Max_height - Chip_heights[i] <= M_vertical * (1 - Max_i[i]);

# non overlapping constraints
subject to Not_overlaps {i in I, j in I: i < j}:
	sum {o in 1..4} Not_overlaps_ind[o,i,j] >= 1;
	
subject to J_is_right {i in I, j in I: i < j}:
	Coordinates_x[i] + widths[i] - Coordinates_x[j] <= M_horizontal * (1 - Not_overlaps_ind[1,i,j]);

subject to J_is_left {i in I, j in I: i < j}:
	Coordinates_x[j] + widths[j] - Coordinates_x[i] <= M_horizontal * (1 - Not_overlaps_ind[2,i,j]);

subject to J_is_up {i in I, j in I: i < j}:
	Coordinates_y[i] + heights[i] - Coordinates_y[j] <= M_vertical * (1 - Not_overlaps_ind[3,i,j]);
	
subject to J_is_down {i in I, j in I: i < j}:
	Coordinates_y[j] + heights[j] - Coordinates_y[i] <= M_vertical * (1 - Not_overlaps_ind[4,i,j]);
