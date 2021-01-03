module motor_shaft(length=24, radius=2.5, flat_offset=1) {
    difference() {
        // main shaft
        cylinder(h=length, r=radius, center=true);
        
        // keyed section
        translate([0 - (flat_offset / 2) + radius,0,0])
            cube([flat_offset + .001, (radius * 2) + .001, length + .001], center=true);
    }
}

$fa = 1;
$fs = 0.4;

// The regulator control cup is defined by it's inside radii (top, bottom),
// height, and thickness
cup_wiggle_room = 0.1;
cup_thickness = 4;
cup_bottom_radius = (27.61 / 2) + cup_wiggle_room;
cup_top_radius =  (26.75 / 2) + cup_wiggle_room;
cup_height = 25.40;

// Motor shaft is defined by the length of the receiver, radius, key offset, and thickness
shaft_length = 20;
shaft_radius = 5;
shaft_key_offset = 0.3;
shaft_thickness = cup_thickness;

// air regulator-motor shaft coupler
// Add cup receiver to shaft receiver
union() {
    // build the cup
    difference() {
        // outside cup
        union() {
            cylinder(h=cup_height, r1=cup_bottom_radius+cup_thickness, 
                     r2=cup_top_radius+cup_thickness, center=true);
            translate([0,0,(cup_thickness/2) + cup_height/2])
                cylinder(h=cup_thickness, r=cup_top_radius+cup_thickness, center=true);
        }
        // inside cup
        cylinder(h=cup_height+.002, r1=cup_bottom_radius, r2=cup_top_radius,
                 center=true);
        // motor shaft (hard to support either way, may as well cut it out
        translate([0, 0, cup_height/2])
            motor_shaft(length = shaft_length, radius = shaft_radius,
                        flat_offset = shaft_key_offset);
    }

    // Move shaft ontop of outside cup
    translate([0, 0, (shaft_length/2) + (cup_height/2) + cup_thickness - .001])
        // build the motor shaft receiver
        difference() {
            // outer cylinder
            cylinder(h = shaft_length, r = shaft_radius + shaft_thickness, 
                     center = true);
            // motor shaft
            motor_shaft(length = shaft_length + .001, radius = shaft_radius,
                        flat_offset = shaft_key_offset);
        }  
}
