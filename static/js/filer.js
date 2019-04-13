$(document).ready(function() {
    $('#input').filer({
      limit: 1,
      maxSize: 10,
      extensions: null,
      changeInput: '<div class="jFiler-input-dragDrop"><div class="jFiler-input-inner"><div class="jFiler-input-icon"><i class="icon-jfi-cloud-up-o"></i></div><div class="jFiler-input-text"><h3>Drag&Drop files here</h3> <span style="display:inline-block; margin: 15px 0">or</span></div><a class="jFiler-input-choose-btn">Browse Files</a></div></div>',
      showThumbs: true,
      appendTo: null,
      theme: "dragdropbox",
      templates: {
          box: '<ul class="jFiler-item-list"></ul>',
          item: '<li class="jFiler-item" style="width: 100%;">\
                      <div class="jFiler-item-container">\
                          <div class="jFiler-item-inner">\
                              <div class="jFiler-item-thumb" style="margin: 0 auto;">\
                                  <div class="jFiler-item-status"></div>\
                                  <div class="jFiler-item-info">\
                                      <span class="jFiler-item-title"><b title="{{fi-name}}">{{fi-name | limitTo: 25}}</b></span>\
                                  </div>\
                                  {{fi-image}}\
                              </div>\
                              <div class="jFiler-item-assets jFiler-row">\
                                  <ul class="list-inline pull-left">\
                                      <li>{{fi-progressBar}}</li>\
                                  </ul>\
                                  <ul class="list-inline pull-right">\
                                      <li><a class="icon-jfi-trash jFiler-item-trash-action"></a></li>\
                                  </ul>\
                              </div>\
                          </div>\
                      </div>\
                  </li>',
          itemAppend: '<li class="jFiler-item" style="width: 100%;">\
                      <div class="jFiler-item-container">\
                          <div class="jFiler-item-inner">\
                              <div class="jFiler-item-thumb" style="margin: 0 auto;">\
                                  <div class="jFiler-item-status"></div>\
                                  <div class="jFiler-item-info">\
                                      <span class="jFiler-item-title"><b title="{{fi-name}}">{{fi-name | limitTo: 25}}</b></span>\
                                  </div>\
                                  {{fi-image}}\
                              </div>\
                              <div class="jFiler-item-assets jFiler-row">\
                                  <ul class="list-inline pull-left">\
                                      <span class="jFiler-item-others">{{fi-icon}} {{fi-size2}}</span>\
                                  </ul>\
                                  <ul class="list-inline pull-right">\
                                      <li><a class="icon-jfi-trash jFiler-item-trash-action"></a></li>\
                                  </ul>\
                              </div>\
                          </div>\
                      </div>\
                  </li>',
          progressBar: '<div class="bar"></div>',
          itemAppendToEnd: false,
          removeConfirmation: false,
          _selectors: {
              list: '.jFiler-item-list',
              item: '.jFiler-item',
              progressBar: '.bar',
              remove: '.jFiler-item-trash-action',
          }
      },
      dragDrop: {
          dragEnter: function(){},
          dragLeave: function(){},
          drop: function(){},
      },
      addMore: false,
      clipBoardPaste: true,
      excludeName: null,
      captions: {
          button: "Choose Files",
          feedback: "Choose files To Upload",
          feedback2: "files were chosen",
          drop: "Drop file here to Upload",
          removeConfirmation: "Are you sure you want to remove this file?",
          errors: {
              filesLimit: "Only {{fi-limit}} files are allowed to be uploaded.",
              filesType: "Only Images are allowed to be uploaded.",
              filesSize: "{{fi-name}} is too large! Please upload file up to {{fi-maxSize}} MB.",
              filesSizeAll: "Files you've choosed are too large! Please upload files up to {{fi-maxSize}} MB."
          }
      }
    })
});
  