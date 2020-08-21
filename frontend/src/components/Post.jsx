import React, { useCallback, useState, useEffect } from 'react';
import TimeAgo from 'react-timeago';

function getThumbClass(spoiler) {
    return spoiler? "thread-thumbnail thumbnail-spoiler" : "thread-thumbnail";
}

function GenericThumbnail(props) {
    return (
        <img className={getThumbClass(props.spoiler)} src={props.thumb_url}/>
    );
}

function AnimatedImageThumbnail(props) {
    const [thumbClass, setThumbClass] = useState(getThumbClass(props.spoiler));
    const [currentSource, setThumbSource] = useState(props.thumb_url);
    function mouseEnterHandler(e) {
        setThumbSource(props.media_url);
        setThumbClass(getThumbClass(false));
    }
    function mouseLeaveHandler(e) {
        setThumbSource(props.thumb_url);
        setThumbClass(getThumbClass(props.spoiler));
    }
    return (
        <img className={thumbClass} src={currentSource} onMouseEnter={mouseEnterHandler} onMouseLeave={mouseLeaveHandler}/>
    );
}

function VideoThumbnail(props) {
    const [thumbClass, setThumbClass] = useState(getThumbClass(props.spoiler));
    function mouseEnterHandler(e) {
        setThumbClass(getThumbClass(false));
        e.target.play();
    }
    function mouseLeaveHandler(e) {
        e.target.pause();
        e.target.currentTime = 0;
        setThumbClass(getThumbClass(props.spoiler));
    }
    return (
        <div className={thumbClass}>
          <video className={thumbClass} loop={true} preload="metadata"
                 onMouseEnter={mouseEnterHandler} onMouseLeave={mouseLeaveHandler} poster={props.thumb_url}>
            <source src={props.media_url} type={props.mimetype}/>
          </video>
        </div>
    );
}

function PostThumbnail(props) {
    let thumbnailImpl;
    if(props.mimetype.startsWith("video")) {
        thumbnailImpl = <VideoThumbnail spoiler={props.spoiler} thumb_url={props.thumb_url} media_url={props.media_url}/>;
    } else if(props.mimetype.startsWith("image") && props.is_animated) {
        thumbnailImpl = <AnimatedImageThumbnail spoiler={props.spoiler} thumb_url={props.thumb_url} media_url={props.media_url}/>;
    } else {
        thumbnailImpl = <GenericThumbnail spoiler={props.spoiler} thumb_url={props.thumb_url}/>;
    }

    const [animatedTextStatus, setAnimatedTextStatus] = useState(false);
    useEffect(() => {
        setAnimatedTextStatus(true);
    }, [animatedTextStatus]);

    const [showSpoilerLabel, setShowSpoilerLabel] = useState(true);
    function mouseEnterHandler(e) {
        if(props.spoiler) {
            setShowSpoilerLabel(false);
        }
    }
    function mouseLeaveHandler(e) {
        if(props.spoiler) {
            setShowSpoilerLabel(true);
        }
    }
    return (
        <div className="col">
          <div className="row">
            <div className="post-thumbnail" onMouseEnter={mouseEnterHandler} onMouseLeave={mouseLeaveHandler}>
              <a className="media-container" href={props.media_url}>
                {props.spoiler && showSpoilerLabel && <span className="spoiler-label text-danger">!</span>}
                {thumbnailImpl}
              </a>
            </div>
          </div>
          {props.spoiler && <div className="col">
                             <div className="row">
                               <small className="text-danger">Media contains spoilers!</small>
                             </div>
                           </div>}
          {props.is_animated && <div className="row">
                                 <noscript>
                                   <small className="text-muted">Animated - click to play</small>
                                 </noscript>
                                 {animatedTextStatus && <small className="text-muted">Animated - click or hover to play</small>} 
                               </div>}
        </div>
    );
}

function ReplyList(props) {
    function emitReply(reply, index) {
        return <a className="post-reply" href={reply.reply_url}>&gt;&gt;{reply.post_id}</a>;
    }
    return (
        <>
          <small className="text-secondary">Replies:</small>
          <div className="post-replies">
            {props.replies.map(emitReply)}
          </div>
        </>
    );
}

export default function Post(props) {
    return (
        <div className="post-container" id={props.post_id}>
          {props.media && <PostThumbnail mimetype={props.mimetype} is_animated={props.is_animated} spoiler={props.spoiler} thumb_url={props.thumb_url} media_url={props.media_url}/>}
          <div className="container-fluid">
            {props.subject && <div className="row">
                                <div className="col"><b>{props.subject}</b></div></div>}
            {props.tags && props.tags.length > 0 && <div className="row">
                         <div className="col">
                           <small className="text-muted">Tags: </small>
                           <small>{props.tags.join(", ")}</small>
                         </div>
                       </div>}
            <div className="row">
              <div className="col-auto">
                <small className="text-secondary">Poster:</small>
                <small className="text-info">{props.poster}</small>
                {props.slip && props.slip.is_admin && <span className="badge badge-danger">Admin</span>}
                {props.slip && !props.slip.is_admin && props.slip.is_mod && <span className="badge badge-success">Mod</span>}
              </div>
              <div className="col-auto">
                <small className="text-secondary">Posted: </small>
                <small className="text-info"><TimeAgo date={props.datetime}/></small>
              </div>
              <div className="col-auto">
                <small className="text-secondary">Post #:</small>
                <small className="text-info">{props.id}</small>
              </div>
              <div className="w-100 d-block d-md-none"></div>
              <div className="col-auto">
                <small><a className="badge badge-primary" href={"#" + props.id}>Permalink</a></small>
              </div>
              {props.slip && (props.slip.is_admin || props.slip.is_mod) && <div className="col-auto">
                                    <details className="badge badge-danger">
                                      <summary>Moderation</summary>
                                      {props.is_op && <a className="mod-item" href={props.move_url}>Move</a>}
                                      <a className="mod-item" href={props.delete_url}>Delete</a>
                                    </details>
                                  </div>}
            </div>
            {props.replies.length > 0 && <div className="row">
                                          <div className="col-auto">
                                            <ReplyList replies={props.replies}/>
                                          </div>
                                        </div>}
            <div className="row post-body" dangerouslySetInnerHTML={{__html: props.body}}></div>
          </div>
        </div>
    );
}
