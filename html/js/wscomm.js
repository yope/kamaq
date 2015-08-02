/* 
 * vim: set tabstop=4:shiftwidth=4
 */

var ws_conn;
var ws_initialized = false;
var ws_fullui = false;

var startTime = (new Date()).getTime();
function log(s)
{
	var ti = (new Date()).getTime() - startTime;
	console.log((ti/1000.0).toFixed(3) + "   : " + s);
}

function WSParseTemp(obj)
{
	if (ws_fullui) {
		add_plot_data(plotdata_t_ext, obj.extruder);
		add_plot_data(plotdata_t_bed, obj.bed);
		draw_plot("canvas_t_ext", plotdata_t_ext);
		draw_plot("canvas_t_bed", plotdata_t_bed);
	} else {
		var t_ext = String(Math.round(obj.extruder * 10) / 10) + "\u00b0C"
		var t_bed = String(Math.round(obj.bed * 10) / 10) + "\u00b0C"
		document.getElementById("div_temp_ext").innerHTML = t_ext;
		document.getElementById("div_temp_bed").innerHTML = t_bed;
	}
}

function WSParseMove(obj)
{
	var p = [obj.x, obj.y];
	var reset = false;
	var type = 1;

	if (obj.z != actual_z) {
		actual_z = obj.z;
		reset = true;
	}
	if (obj.e <= actual_e) {
		log("Type 0");
		type = 0;
	}
	actual_e = obj.e;
	var p = [obj.x, obj.y, obj.z, type];
	add_plot_data(plotdata_mov, p, reset);
	draw_movements("canvas_mov", plotdata_mov);
	document.getElementById("div_log_posx").innerHTML = obj.x;
	document.getElementById("div_log_posy").innerHTML = obj.y;
	document.getElementById("div_log_posz").innerHTML = obj.z;
	document.getElementById("div_log_pose").innerHTML = obj.e;
}

var printer_status = "idle";
var extruder_status = "off";
var bed_status = "off";

function WSParseStatus(obj)
{
	printer_status = obj.motors;
	extruder_status = obj.extruder;
	bed_status = obj.bed;
	var divm = document.getElementById("div_motor_status");
	var dive = document.getElementById("div_ext_status");
	var divb = document.getElementById("div_bed_status");

	log("Status: " + printer_status + " " + extruder_status + " " + bed_status);
	if (printer_status == "idle") {
		block_move_buttons(false);
	} else {
		block_move_buttons(true);
	}
	divm.innerHTML = "Printer: " + printer_status;
	dive.innerHTML = "Hotend: " + extruder_status;
	divb.innerHTML = "Bed: " + bed_status;
	if ((extruder_status.indexOf("ok") < 0) && (extruder_status.indexOf("off") < 0))
		dive.style.backgroundColor = "red";
	else
		dive.style.backgroundColor = "green";
	if ((bed_status.indexOf("ok") < 0) && (bed_status.indexOf("off") < 0))
		divb.style.backgroundColor = "red";
	else
		divb.style.backgroundColor = "green";
}

function WSParseLog(obj)
{
	var elem = document.getElementById("div_log_" + obj.type);

	if (undefined !== elem)
		elem.innerHTML = obj.value;

	if (obj.type == "layer_count") {
		UISetLayerCount(obj.value);
	} else if (obj.type == "layer") {
		UISetLayerNum(obj.value);
	}
}

function WSParseSetpoint(obj)
{
	var id_entry = "heater_" + obj.type + "_entry";
	var id_check = "heater_" + obj.type + "_check";

	if (obj.value == 0) {
		document.getElementById(id_check).checked = false;
	} else {
		document.getElementById(id_check).checked = true;
		document.getElementById(id_entry).value = obj.value;
	}
}

function WSHandler(txt)
{
	var obj = JSON.parse(txt.data);
	var id = obj.id;

	// log(txt.data);

	switch(id) {
	case "temperature":
		WSParseTemp(obj);
		break;
	case "move":
		WSParseMove(obj);
		break;
	case "status":
		WSParseStatus(obj);
		break;
	case "log":
		WSParseLog(obj);
		break;
	case "setpoint":
		WSParseSetpoint(obj);
		break;
	default:
		break;
	}
}

function WSInit(full)
{
	ws_conn = new WebSocket("ws://"+window.location.hostname+":9999/");
	ws_conn.onopen = function () {
		ws_fullui = full;
		ws_initialized = true;
		if (full)
			WSSendObject(new WSCommand("hello"));
		else
			WSSendObject(new WSCommand("hi"));
	}
	ws_conn.onmessage = WSHandler;
}

function WSCommand(cmd)
{
	this.command = cmd;
}

function WSSendObject(obj)
{
	var txt = JSON.stringify(obj);
	ws_conn.send(txt);
}


