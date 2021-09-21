import React, { useState, useEffect }  from 'react';
import Modal from 'react-modal';

function ModalBase(props) {
    const [renderingModal, setRenderingModal] = useState(false);
    const [modalOpen, setModalOpen] = useState(props.modal_open);
    // useEffect() only runs on the client/browser, so use that to ensure
    // the modal is only rendered on the client (react-modal has
    // bug issues when attempting to use SSR)
    useEffect(() => {
        if(renderingModal == false) {
            setRenderingModal(true);
            const menuLink = document.getElementById(props.menu_id);
            menuLink.addEventListener("click", function(e) {
                e.preventDefault();
                setModalOpen(true);
            });
        }
    });
    return (
        <React.Fragment>
          {renderingModal && <Modal
                              className="modal"
                              overlayClassName="modal-overlay"
                              isOpen={modalOpen}
                              onRequestClose={() => {setModalOpen(false);}}>
                              <React.Fragment>
                                {props.children}
                                <div className="row">
                                  <input type="submit" className="m-1 btn btn-primary" htmlFor={props.form_id}
                                         onClick={() => document.getElementById(props.form_id).submit()} value="Post"/>
                                  <button className="m-1 btn btn-secondary" onClick={() => setModalOpen(false)}>Close</button>
                                </div>
                              </React.Fragment>
                            </Modal>
           }
        </React.Fragment>
    );
}

export default ModalBase;
