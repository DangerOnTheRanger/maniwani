import React, { useState, useEffect }  from 'react';
import Modal from 'react-modal';
import { NewPostForm } from './PostForm';

function buildAction(threadId) {
    return '/threads/' + threadId + '/new';
}

function NewPostModal(props) {
    const [renderingModal, setRenderingModal] = useState(false);
    const [modalOpen, setModalOpen] = useState(props.modal_open);
    // useEffect() only runs on the client/browser, so use that to ensure
    // the modal is only rendered on the client (react-modal has
    // bug issues when attempting to use SSR)
    useEffect(() => {
        if(renderingModal == false) {
            setRenderingModal(true);
            // TODO: can this be split off into a separate function?
            const postLink = document.getElementById('newPostLink');
            postLink.addEventListener("click", function(e) {
                e.preventDefault();
                setModalOpen(true);
            });
        }
    });
    return (
        <React.Fragment>
          {renderingModal && <Modal
                              isOpen={modalOpen}
                              onRequestClose={() => {setModalOpen(false);}}>
                              <React.Fragment>
                                <NewPostForm action={buildAction(props.thread_id)} {...props}/>
                                <div className="row">
                                  <input type="submit" className="m-1 btn btn-primary" htmlFor="postForm" onClick={() => {document.getElementById('postForm').submit();}} value="Post"/>
                                  <button className="m-1 btn btn-secondary" onClick={() => {setModalOpen(false);}}>Close</button>
                                </div>
                              </React.Fragment>
                            </Modal>
           }
        </React.Fragment>
    );
}

export default NewPostModal;
