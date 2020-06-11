import axios from 'axios';

var threadSubscriptions = new Map();
var boardSubscriptions = new Map();
var ports = [];
var eventPump = null;
var clientId = null;
var preConnectionQueue = new Array();


function initPump() {
	eventPump = new EventSource("/api/v1/live");
	eventPump.addEventListener("new-client", function(e) {
		clientId = e.data;
		console.log("got new-client message");
		console.log(e.data);
		console.log("clientId now:");
		console.log(clientId);
		eventPump.addEventListener("new-post", handleNewPost);
		eventPump.addEventListener("new-reply", handleNewReply);
		eventPump.addEventListener("new-thread", handleNewThread);
		preConnectionQueue.forEach(sendServerMessage);
		console.log("eventsource setup complete");
	});
}

function handleThreadSubscribe(e, port, params) {
	if(threadSubscriptions.has(params.thread) == false) {
		console.log("performing initial subscription setup");
		let serverParams = {"client-id": clientId,
							"subscribe": {"thread": [params.thread]}
						   };
		sendServerMessage(serverParams);
		threadSubscriptions.set(params.thread, new Array());
	}
	console.log("port:");
	console.log(port);
	threadSubscriptions.get(params.thread).push(port);
	console.log("added subscription - threadSubscriptions now:");
	console.log(threadSubscriptions);
	
}
function handleBoardSubscribe(e, port, params) {
	if(boardSubscriptions.has(params.board) == false) {
		let serverParams = {"client-id": clientId,
							"subscribe": {"board": [params.board]}
						   };
		sendServerMessage(serverParams);
		boardSubscriptions.set(params.board, new Array());
	}
	boardSubscriptions.get(params.board).push(port);
}

function handleNewReply(e) {
	let eventData = JSON.parse(e.data);
	let threadId = eventData.thread;
	threadSubscriptions[threadId].forEach(function(port) {
		port.postMessage({"message": "reply", "thread": threadId, "reply-to": eventData.reply_to, "post": eventData.post});
	});
}

function handleNewPost(e) {
	let eventData = JSON.parse(e.data);
	let threadId = eventData.thread;
	console.log("got new post");
	console.log(eventData.post);
	//console.log(threadSubscriptions[threadId]);
	console.log("eventData:");
	console.log(eventData);
	console.log("THREADSUBSCRIPTIONS:");
	console.log(threadSubscriptions);
	threadSubscriptions.get(threadId).forEach(function(port) {
		console.log("sending update");
		port.postMessage({"message": "new-post", "thread": threadId, "post": eventData.post});
	});
}

function handleNewThread(e) {
	let eventData = JSON.parse(e.data);
	let threadId = eventData.thread;
	let boardId = eventData.board;
	boardSubscriptions[boardId].forEach(function(port) {
		port.postMessage({"message": "new-thread", "thread": threadId, "board": boardId});
	});
}

function sendServerMessage(data) {
	if(clientId != null) {
		data["client-id"] = clientId;
		console.log("sending server message");
		console.log(data);
		axios.post("/api/v1/live", data);
	} else {
		preConnectionQueue.push(data);
	}
}

onconnect = function(e) {
	console.log("got connection");
	if(eventPump == null) {
		initPump();
	}
	let port = e.ports[0];
	ports.push(port);
	port.onmessage = function(e) {
		let data = e.data;
		console.log("got message " + data.message);
		switch(data.message) {
		case "subscribe-thread":
			handleThreadSubscribe(e, port, data);
			break;
		case "subscribe-board":
			handleBoardSubscribe(e, port, data);
			break;
		}
	};
	port.postMessage({"message": "debug", "content": "shared worker connection successful"});
}

console.log("web worker loaded");
