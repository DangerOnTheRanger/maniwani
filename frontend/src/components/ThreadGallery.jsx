import React from 'react';

function ThreadGallery(props) {
    return (
        <div className="media-grid">
          {props.posts.map((post, i) => {
              const bgStyle = {backgroundImage: "url(" + post.thumb_url + ")"};
              return <a href={post.media_url}><div style={bgStyle} className="media-element">
                     </div></a>;
          })}
        </div>);
}

export default ThreadGallery;
