import React from 'react';
import ReactDOM from 'react-dom';
import Thread from '../components/Thread';

const thread_data = window._THREAD;
ReactDOM.hydrate(<Thread {...thread_data}/>, document.getElementById('thread-container'));
