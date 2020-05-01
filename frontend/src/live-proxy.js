const axios = require('axios');

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
		eventPump.addEventListener("new-post", handleNewPost);
		eventPump.addEventListener("new-reply", handleNewReply);
		eventPump.addEventListener("new-thread", handleNewThread);
		preConnectionQueue.forEach(sendServerMessage);
	});
}

onconnect = function(e) {
	if(eventPump == null) {
		initPump();
	}
	let port = e.ports[0];
	ports.push(port);
	port.start();
}

function handleThreadSubscribe(e, params) {
	if(threadSubscriptions.has(params.thread) == false) {
		threadSubscriptions.set(params.thread, new Array());
	}
	let port = e.ports[0];
	threadSubscriptions.get(params.thread).push(port);
	let serverParams = {"client-id": clientId,
						"subscribe": {"thread": [params.thread]}
					   };
	sendServerMessage(serverParams);
}
function handleBoardSubscribe(e, params) {
	if(boardSubscriptions.has(params.board) == false) {
		boardSubscriptions.set(params.board, new Array());
	}
	let port = e.ports[0];
	boardSubscriptions.get(params.board).push(port);
	let serverParams = {"client-id": clientId,
						"subscribe": {"board": [params.board]}
					   };
	sendServerMessage(serverParams);
}

function handleNewReply(e) {
	let eventData = JSON.parse(e.data);
	let threadId = eventData.thread;
	threadSubscriptions[threadId].forEach(function(port) {
		port.postMessage({"thread": threadId, "reply-to": eventData.reply_to, "post": eventData.post});
	});
}

function handleNewPost(e) {
	let eventData = JSON.parse(e.data);
	let threadId = eventData.thread;
	threadSubscriptions[threadId].forEach(function(port) {
		port.postMessage({"thread": threadId, "post": eventData.post});
	});
}

function handleNewThread(e) {
	let eventData = JSON.parse(e.data);
	let threadId = eventData.thread;
	let boardId = eventData.board;
	boardSubscriptions[boardId].forEach(function(port) {
		port.postMessage({"thread": threadId, "board": boardId});
	});
}


function sendServerMessage(data) {
	if(clientId != null) {
		axios.post("/api/v1/live", data);
	} else {
		preConnectionQueue.push(data);
	}
}

onmessage = function(e) {
	let data = e.data;
	switch(data.message) {
	case "subscribe-thread":
		handleThreadSubscribe(e, data);
		break;
	case "subscribe-board":
		handleBoardSubscribe(e, data);
		break;
	}
}
