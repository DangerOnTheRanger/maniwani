import React from 'react';
import { connect } from 'react-redux';

function ThreadThumbnail(props) {
    var bgStyle = "bg-light";
    var textStyle = "text-body";
    if(props.tags) {
        const mainTag = props.tags[0];
        if(mainTag in props.tag_styles) {
            if(props.tag_styles[mainTag].bg_style) {
                bgStyle = props.tag_styles[mainTag].bg_style;
            }
            if(props.tag_styles[mainTag].text_style) {
                textStyle = props.tag_styles[mainTag].text_style;
            }
        }
    }
    var imageClass = props.spoiler? "catalog-thumbnail thumbnail-spoiler" : "catalog-thumbnail";
    return (
        <a href={props.thread_url} className={"thread " + bgStyle}>
          <div className="catalog-media-container">
            {props.spoiler && <span className="spoiler-label text-danger">!</span>}
            <img className={imageClass} src={props.thumb_url}/>
          </div>
          <div className="p-1">
            {props.subject && <h6 className={"text-center font-weight-bold " + textStyle}>{props.subject}</h6>}
            {!props.subject && <h6 className="text-center text-muted">No subject</h6>}
          </div>
          <div className="pb-2 pl-4 pr-4">
            <div className={"thread-body " + textStyle} dangerouslySetInnerHTML={{__html: props.body}}>
            </div>
          </div>
          <span className={"thread-stats-container " + textStyle}>
            {props.display_board && <small>/</small>}
            {props.display_board && <small>{props.board}</small>}
            {props.display_board && <small>/</small> && ' '}
            <i className="fas fa-comment"></i>{props.num_replies}
            &nbsp;
            <i className="fas fa-image"></i>{props.num_media}
          </span>
        </a>
    );
}

function mapStateToProps(state) {
    return {threads: state.threads, display_board: state.catalogInfo.board,
            tag_styles: state.catalogInfo.styles};
}

function Catalog(props) {
    return (
        <div className="container-fluid">
          <div className="catalog-grid">
            {props.threads.map((thread, i) => {
                return <ThreadThumbnail {...thread} display_board={props.display_board} tag_styles={props.tag_styles}/>;
            })}
          </div>
        </div>
    );
}

export default connect(mapStateToProps)(Catalog);
