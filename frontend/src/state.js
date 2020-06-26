const NEW_POST = 'NEW_POST';
const NEW_THREAD = 'NEW_THREAD';
const SET_BOARD = 'SET_BOARD';
const SET_STYLES = 'SET_STYLES';
const DEFAULT_STATE = {posts: [], threads: [], catalogInfo: {board: "", styles: []}};

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
function setBoard(board) {
	return {type: SET_BOARD, board};
}
function setStyles(styles) {
	return {type: SET_STYLES, styles};
}

export { newPost, newThread, setBoard, setStyles, reducer, DEFAULT_STATE};
