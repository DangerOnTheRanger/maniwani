import React from 'react';

function ThreadGallery(props) {
    return (
        <div className="media-grid">
          {props.posts.map((post, i) => {
              const bgStyle = {backgroundImage: "url(" + post.media + ")"};
              return <a href={post.media}><div style={bgStyle} className="media-element">
                     </div></a>;
          })}
        </div>);
}

export default ThreadGallery;
