import React from 'react';

function BoardIndex(props) {
    return (<div className="media-grid">
              {props.boards.map((board, i) => {
                  let boardStyle = {};
                  if(board.media) {
                      boardStyle = {backgroundImage: "url(" + board.thumb_url + ")"};
                  }
                  return <a href={board.catalog_url}>
                           <div style={boardStyle} className="board-entry">
                             <span className="board-label">/{board.name}/</span>
                           </div>
                         </a>;
              })}
            </div>);
}

export default BoardIndex;
