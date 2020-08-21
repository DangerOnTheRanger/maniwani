import React, { useState, useEffect }  from 'react';
import ModalBase from './ModalBase';
import { NewThreadForm } from './PostForm';

function NewThreadModal(props) {
    return (
        <ModalBase menu_id="newThreadLink" form_id="postForm">
          <NewThreadForm action="/threads/new" {...props}/>
        </ModalBase>
    );
}

export default NewThreadModal;
