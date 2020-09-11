const NEW_POST = 'NEW_POST';
const NEW_THREAD = 'NEW_THREAD';
const DELETE_THREAD = 'DELETE_THREAD';
const SET_BOARD = 'SET_BOARD';
const SET_STYLES = 'SET_STYLES';
const SET_CAPTCHA = 'SET_CAPTCHA';
const DEFAULT_STATE = {posts: [], threads: [], captcha: {}, catalogInfo: {board: "", styles: []}};

function reducer(state = DEFAULT_STATE, action) {
	switch(action.type) {
	case NEW_POST:
		return Object.assign({}, state, {
			posts: [
				...state.posts,
				action.post
			]});
	case NEW_THREAD:
		return Object.assign({}, state, {
			threads: [
				action.thread,
				...state.threads
			]});
	case DELETE_THREAD:
		return Object.assign({}, state, {
			threads: [...state.threads].filter(thread => thread.id != action.id)
		});
	case SET_BOARD:
		return Object.assign({}, state, {
			catalogInfo: {
				board: action.board,
				styles: state.styles
			}});
	case SET_STYLES:
		return Object.assign({}, state, {
			catalogInfo: {
				styles: action.styles,
				board: state.board
			}});
	case SET_CAPTCHA:
		return Object.assign({}, state, {captcha: action.captcha});
	default:
		return state;
	}
}

function newPost(post) {
	return {type: NEW_POST, post};
}
function newThread(thread) {
	return {type: NEW_THREAD, thread};
}
function deleteThread(id) {
	return {type: DELETE_THREAD, id};
}
function setBoard(board) {
	return {type: SET_BOARD, board};
}
function setStyles(styles) {
	return {type: SET_STYLES, styles};
}
function setCaptcha(captcha) {
	return {type: SET_CAPTCHA, captcha};
}

export { newPost, newThread, deleteThread, setBoard, setStyles, setCaptcha, reducer, DEFAULT_STATE};
