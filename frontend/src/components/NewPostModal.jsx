import React, { useState, useEffect }  from 'react';
import { connect } from 'react-redux';
import ModalBase from './ModalBase';
import { NewPostForm } from './PostForm';


function buildAction(threadId) {
    return '/threads/' + threadId + '/new';
}

function mapStateToProps(state) {
    return {...state.captcha};
}

function NewPostModal(props) {
    return (
        <ModalBase menu_id="newPostLink" form_id="postForm">
          <NewPostForm action={buildAction(props.thread_id)} {...props}/>
        </ModalBase>
    );
}

export default connect(mapStateToProps)(NewPostModal);
