import {isarray, count, argsForEach} from "../../../lib-independent-of-src/owned/primitive_data_util"
import {LogType} from "../../globals";

// any helper functions used in macro defs must somehow be made globally accessible
declare const window : any;
window.argsForEach = argsForEach;
window.isarray = isarray;
window.count = count;
window.CONSOLE_WARN_STYLE = 'background: black; color: yellow; fontsize:medium;';
window.CONSOLE_NOTICE_STYLE = 'background: black; color: white;';
window.CONSOLE_DEBUG_STYLE = 'background: black; color: white; fontsize:large;';
window.CONSOLE_TODO_STYLE = 'background: white; color: green;';
window.CONSOLE_REMIND_STYLE = 'background: white; color: purple;';

export function devthrow(e:Error) {
	throw(e);
}

export function weakassert(test:boolean, msg?:string, ...args_for_console:any[]) {
	if ( window.structure_together.assertions_enabled && !(test)) {
		console.error(args_for_console);

		if (msg) {
			console.error("Failed assertion %test%\n" + msg + "\n");
		}
		else {
			console.error("Failed assertion %test%\n");
		}
	}
}

export function dassert(test:boolean, msg?:string, ...args_for_console:any[]) {
	if ( window.structure_together.assertions_enabled && !(test)) {
		console.error(args_for_console);

		if (msg) {
			throw new Error("Failed assertion %test%\n" + msg + "\n");
		}
		else {
			throw new Error("Failed assertion %test%\n");
		}
	}
}


// ------------- BEGIN d(log|warn|err) -------------

export function dlog(...args_for_console:any[]) {
	console.log(args_for_console);
}

export function dwarn(...args_for_console:any[]) {
	console.warn(args_for_console);
}

export function derr(...args_for_console:any[]) {
	console.error(args_for_console);
}

export function ddeb(x:string, ...args:any[]) {
	console.warn("%c"+x, window.CONSOLE_DEBUG_STYLE, args);
}

export function dremind(x:string, ...args:any[]) {
	console.warn("%c"+x, window.CONSOLE_REMIND_STYLE, args);
}

export function dremindonce(x:string, ...args:any[]) {
	window.remindonce(x, args);
}

export function dtodo(x:string, ...args:any[]) {
	console.warn("%c"+x, window.CONSOLE_TODO_STYLE, args);
}

export function dnote(x:string, ...args:any[]) {
	console.warn("%c"+x, window.CONSOLE_NOTICE_STYLE, args);
}


// ------------- BEGIN d(log|warn|err)cat -------------

export function dlogcat(cat:LogType, ...args_for_console:any[]) {
	if (window.structure_together.logging.logTypeActive(cat)) {
		console.log(args_for_console);
	}
}

export function dwarncat(cat:LogType, ...args_for_console:any[]) {
	if (window.structure_together.logging.logTypeActive(cat)) {
		console.warn(args_for_console);
	}
}

export function derrcat(cat:LogType, ...args_for_console:any[]) {
	if (window.structure_together.logging.logTypeActive(cat)) {
		console.error(args_for_console);
	}
}


// ------------- BEGIN d(log|warn|err)if -------------


export function dlogif(cond:boolean, ...args_for_console:any[]) {
	if (cond) {
		console.log(args_for_console);
	}
}

export function dwarnif(cond:boolean, ...args_for_console:any[]) {
	if (cond) {
		console.warn(args_for_console);
	}
}

export function derrif(cond:boolean, ...args_for_console:any[]) {
	if (cond) {
		console.error(args_for_console);
	}
}

export function assert_nt(...exprs:any[]) {
	if ( window.structure_together.assertions_enabled ) {
		argsForEach((x, i) => {
			if (x === null || x === undefined) {
				throw new Error("Element " + i.toString() + " of (%exprs%) should not be null or undefined.");
			}
		}, exprs);
	}
}

//noSTOP

export function timerStart(label:string) {
	if( window.structure_together.logging.logTypeActive('timer') ) {		
		window.std.timer.start(label);
	}
}

export function timerEnd(label:string) {
	if( window.structure_together.logging.logTypeActive('timer') ) {
		const elapsed = Math.floor(window.std.timer.end(label));
		if( elapsed >= window.std.timer.min_to_display ) {
			console.log("%c" + label + ": " + elapsed + "ms", "color:blue;");
		}
	}
}