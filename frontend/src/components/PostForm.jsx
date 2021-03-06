import React from 'react';

function NewThreadForm(props) {
    return (<React.Fragment>
             <PostFormBase tag_entry={true} {...props}/>
             <input type="hidden" form="postForm" name="board" value={props.board_id}/>
            </React.Fragment>);
}

function NewPostForm(props) {
    return (<React.Fragment>
              <PostFormBase tag_entry={false} {...props}/>
             <input type="hidden" form="postForm" name="thread" value={props.thread_id}/>
            </React.Fragment>);
}

function PostFormBase(props) {
	return (
		<form id="postForm" method="post" encType="multipart/form-data" action={props.action}>
          <div className="form-group">
            <label htmlFor="subject">Subject</label>
            <input className="form-control" type="text" id="subject" name="subject"/>
          </div>
          {props.privileged_slip && <SlipEntry/>}
          {props.tag_entry && <TagEntry/>}
          <div className="form-group">
            <label htmlFor="body">Body</label>
            <textarea className="form-control" id="body" name="body"/>
          </div>
          <div className="form-group">
            <div className="form-check">
              <input type="checkbox" className="form-check-input" id="spoiler" name="spoiler" value="true"/>
              <label htmlFor="spoiler" className="form-check-label">Spoiler?</label>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="media">Media upload</label>
            <input type="file" id="media" name="media"/>
            <small className="form-text text-muted">Maximum attachment size: { props.max_upload_size }. Check
              the rules to see what kind of files can be uploaded.</small>
          </div>
          {props.embed_submit && <input type="submit" className="m-1 btn btn-primary" value="Post"/>}
          {props.captcha_method === 'CAPTCHOULI' &&
           <Captchouli captchouli_id={props.captcha_id} character={props.character} images={props.images}/>}
		</form>
	);
}

function TagEntry(props) {
    return (
        <div className="form-group">
          <label htmlFor="tags">Tags</label>
          <input type="text" className="form-control" id="tags" name="tags"/>
          <small className="form-text text-muted">Enter tags for this thread separated by commas.</small>
        </div>
    );
}

function SlipEntry(props) {
    return (
        <div className="form-check">
          <input type="checkbox" className="form-check-input" id="useslip" name="useslip" value="true"/>
          <label htmlFor="useslip" className="form-check-label"/>
          <small className="form-text text-muted">This will only have an effect if your slip
            has special permissions enabled for this board (admin, mod, etc.).
          </small>
        </div>
    );
}

function Captchouli(props) {
    return (
        <React.Fragment>
        <input type="hidden" name="captchouli-id" value={props.captchouli_id}></input>
          <details>
            <summary className="text-muted">Select all images of <b>{props.character}</b></summary>
            <div className="captchouli-container">
              {Object.entries(props.images).map(([name, src]) => {
                  return <div className="captchouli-input">
                           <label>
                             <input type="checkbox" className="captchouli-checkbox" name={name} autoComplete="off"/>
                             <img className="captchouli-img" draggable="false" src={src}/>
                           </label>
                         </div>;
              })}
            </div>
          </details>
        </React.Fragment>
    );
}

export { NewThreadForm, NewPostForm };
