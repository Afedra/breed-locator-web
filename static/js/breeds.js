!function(a,b,c){function d(b,c){this.element=a(b),this.settings=a.extend({},f,c),this._defaults=f,this._name=e,this.init()}var e="metisMenu",f={toggle:!0,doubleTapToGo:!1};d.prototype={init:function(){var b=this.element,d=this.settings.toggle,f=this;this.isIE()<=9?(b.find("li.active").has("ul").children("ul").collapse("show"),b.find("li").not(".active").has("ul").children("ul").collapse("hide")):(b.find("li.active").has("ul").children("ul").addClass("collapse in"),b.find("li").not(".active").has("ul").children("ul").addClass("collapse")),f.settings.doubleTapToGo&&b.find("li.active").has("ul").children("a").addClass("doubleTapToGo"),b.find("li").has("ul").children("a").on("click."+e,function(b){return b.preventDefault(),f.settings.doubleTapToGo&&f.doubleTapToGo(a(this))&&"#"!==a(this).attr("href")&&""!==a(this).attr("href")?(b.stopPropagation(),void(c.location=a(this).attr("href"))):(a(this).parent("li").toggleClass("active").children("ul").collapse("toggle"),void(d&&a(this).parent("li").siblings().removeClass("active").children("ul.in").collapse("hide")))})},isIE:function(){for(var a,b=3,d=c.createElement("div"),e=d.getElementsByTagName("i");d.innerHTML="<!--[if gt IE "+ ++b+"]><i></i><![endif]-->",e[0];)return b>4?b:a},doubleTapToGo:function(a){var b=this.element;return a.hasClass("doubleTapToGo")?(a.removeClass("doubleTapToGo"),!0):a.parent().children("ul").length?(b.find(".doubleTapToGo").removeClass("doubleTapToGo"),a.addClass("doubleTapToGo"),!1):void 0},remove:function(){this.element.off("."+e),this.element.removeData(e)}},a.fn[e]=function(b){return this.each(function(){var c=a(this);c.data(e)&&c.data(e).remove(),c.data(e,new d(this,b))}),this}}(jQuery,window,document);

$(function () {
  var page_title = $(document).attr("title");

  function hide_stream_update() {
    $(".stream-update").hide();
    $(".stream-update .new-breeds").text("");
    $(document).attr("title", page_title);
  };

  $("body").keydown(function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
    if (evt.ctrlKey && keyCode == 80) {
      $(".btn-compose").click();
      return false;
    }
  });

  $("#compose-form textarea[name='post']").keydown(function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
    if (evt.ctrlKey && (keyCode == 10 || keyCode == 13)) {
      $(".btn-breed").click();
    }
  });

  $(".btn-compose").click(function () {
    if ($(".compose").hasClass("composing")) {
      $(".compose").removeClass("composing");
    }
    else {
      $(".compose").addClass("composing");
      $(".compose textarea").val("");
    }
  });

  $(".btn-breed").click(function () {
    var last_breed = $(".stream li:first-child").attr("breed-id");
    if (last_breed == undefined) {
      last_breed = "0";
    }
    $("#compose-form input[name='last_breed']").val(last_breed);
    $.ajax({
      url: '/breeds/breed/',
      data: $("#compose-form").serialize(),
      type: 'post',
      cache: false,
      success: function (data) {
        $("ul.stream").prepend(data);
        $(".compose").removeClass("composing");
        hide_stream_update();
      }
    });
  });

  $("ul.stream").on("click", ".match", function () {
    var li = $(this).closest("li");
    var breed = $(li).attr("breed-id");
    var csrf = $(li).attr("csrf");
    $.ajax({
      url: '/breeds/match/',
      data: {
        'breed': breed,
        'csrfmiddlewaretoken': csrf
      },
      type: 'post',
      cache: false,
      success: function (data) {
        if ($(".match", li).hasClass("unmatch")) {
          $(".match", li).removeClass("unmatch");
          $(".match .text", li).text("Match");
        }
        else {
          $(".match", li).addClass("unmatch");
          $(".match .text", li).text("Unmatch");
        }
        $(".match .match-count", li).text(data);
      }
    });
    return false;
  });

  $("ul.stream").on("click", ".comment", function () { 
    var breed = $(this).closest(".breed");
    if ($(".comments", breed).hasClass("tracking")) {
      $(".comments", breed).slideUp();
      $(".comments", breed).removeClass("tracking");
    }
    else {
      $(".comments", breed).show();
      $(".comments", breed).addClass("tracking");
      $(".comments input[name='post']", breed).focus();
      var breed = $(breed).closest("li").attr("breed-id");
      $.ajax({
        url: '/breeds/comment/',
        data: { 'breed': breed },
        cache: false,
        beforeSend: function () {
          $("ol", breed).html("<li class='loadcomment'><img src='/static/img/loading.gif'></li>");
        },
        success: function (data) {
          $("ol", breed).html(data);
          $(".comment-count", breed).text($("ol li", breed).not(".empty").length);
        }
      });
    }
    return false;
  });

  $("ul.stream").on("keydown", ".comments input[name='post']", function (evt) {
    var keyCode = evt.which?evt.which:evt.keyCode;
    if (keyCode == 13) {
      var form = $(this).closest("form");
      var container = $(this).closest(".comments");
      var input = $(this);
      $.ajax({
        url: '/breeds/comment/',
        data: $(form).serialize(),
        type: 'post',
        cache: false,
        beforeSend: function () {
          $(input).val("");
        },
        success: function (data) {
          $("ol", container).html(data);
          var breed_container = $(container).closest(".breed");
          $(".comment-count", breed_container).text($("ol li", container).length);
        }
      });
      return false;
    }
  });

  var load_breeds = function () {
    if (!$("#load_breed").hasClass("no-more-breeds")) {
      var page = $("#load_breed input[name='page']").val();
      var next_page = parseInt($("#load_breed input[name='page']").val()) + 1;
      $("#load_breed input[name='page']").val(next_page);
      $.ajax({
        url: '/breeds/load/',
        data: $("#load_breed").serialize(),
        cache: false,
        beforeSend: function () {
          $(".load").show();
        },
        success: function (data) {
          if (data.length > 0) {
            $("ul.stream").append(data)
          }
          else {
            $("#load_breed").addClass("no-more-breeds");
          }
        },
        complete: function () {
          $(".load").hide();
        }
      });
    }
  };

  $("#load_breed").bind("enterviewport", load_breeds).bullseye();

  function check_new_breeds () {
    var last_breed = $(".stream li:first-child").attr("breed-id");
    var breed_source = $("#breed_source").val();
    if (last_breed != undefined) {
      $.ajax({
        url: '/breeds/check/',
        data: {
          'last_breed': last_breed,
          'breed_source': breed_source
        },
        cache: false,
        success: function (data) {
          if (parseInt(data) > 0) {
            $(".stream-update .new-breeds").text(data);
            $(".stream-update").show();
            $(document).attr("title", "(" + data + ") " + page_title);
          }
        },
        complete: function() {
          window.setTimeout(check_new_breeds, 30000);
        }
      });
    }
    else {
      window.setTimeout(check_new_breeds, 30000);
    }
  };
  check_new_breeds();

  $(".stream-update a").click(function () {
    var last_breed = $(".stream li:first-child").attr("breed-id");
    var breed_source = $("#breed_source").val();
    $.ajax({
      url: '/breeds/load_new/',
      data: { 
        'last_breed': last_breed,
        'breed_source': breed_source
      },
      cache: false,
      success: function (data) {
        $("ul.stream").prepend(data);
      },
      complete: function () {
        hide_stream_update();
      }
    });
    return false;
  });

  $("input,textarea").attr("autocomplete", "off");

  function update_breeds () {
    var first_breed = $(".stream li:first-child").attr("breed-id");
    var last_breed = $(".stream li:last-child").attr("breed-id");
    var breed_source = $("#breed_source").val();

    if (first_breed != undefined && last_breed != undefined) {
      $.ajax({
        url: '/breeds/update/',
        data: {
          'first_breed': first_breed,
          'last_breed': last_breed,
          'breed_source': breed_source
        },
        cache: false,
        success: function (data) {
          $.each(data, function(id, breed) {
              var li = $("li[breed-id='" + id + "']");
              $(".match-count", li).text(breed.matches);
              $(".comment-count", li).text(breed.comments);
          });
        },
        complete: function () {
          window.setTimeout(update_breeds, 30000);
        }
      });
    }
    else {
      window.setTimeout(update_breeds, 30000);
    }
  };
  update_breeds();

  function track_comments () {
    $(".tracking").each(function () {
      var container = $(this);
      var breed = $(this).closest("li").attr("breed-id");
      $.ajax({
        url: '/breeds/track_comments/',
        data: {'breed': breed},
        cache: false,
        success: function (data) {
          $("ol", container).html(data);
          var breed_container = $(container).closest(".breed");
          $(".comment-count", breed_container).text($("ol li", container).length);
        }
      });
    });
    window.setTimeout(track_comments, 30000);
  };
  track_comments();

  $("ul.stream").on("click", ".remove-breed", function () {
    var li = $(this).closest("li");
    var breed = $(li).attr("breed-id");
    var csrf = $(li).attr("csrf");
    $.ajax({
      url: '/breeds/remove/',
      data: {
        'breed': breed,
        'csrfmiddlewaretoken': csrf
      },
      type: 'post',
      cache: false,
      success: function (data) {
        $(li).fadeOut(400, function () {
          $(li).remove();
        });
      }
    });
  });

  $("#compose-form textarea[name='post']").keyup(function () {
    $(this).count(255);
  });

});
$(function() {
  $('#side-menu').metisMenu();
});

//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
// Sets the min-height of #page-wrapper to window size
$(function() {
  $(window).bind("load resize", function() {
      var topOffset = 50;
      var width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
      if (width < 768) {
          $('div.navbar-collapse').addClass('collapse');
          topOffset = 100; // 2-row-menu
      } else {
          $('div.navbar-collapse').removeClass('collapse');
      }

      var height = ((this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height) - 1;
      height = height - topOffset;
      if (height < 1) height = 1;
      if (height > topOffset) {
          $("#page-wrapper").css("min-height", (height) + "px");
      }
  });

  var url = window.location;
  // var element = $('ul.nav a').filter(function() {
  //     return this.href == url;
  // }).addClass('active').parent().parent().addClass('in').parent();
  var element = $('ul.nav a').filter(function() {
      return this.href == url;
  }).addClass('active').parent();

  while (true) {
      if (element.is('li')) {
          element = element.parent().addClass('in').parent();
      } else {
          break;
      }
  }
});
$(document).ready(function() {
  $('#input').filer({
    limit: 1,
    maxSize: 10,
    extensions: null,
    changeInput: '<div class="jFiler-input-dragDrop"><div class="jFiler-input-inner"><div class="jFiler-input-icon"><i class="icon-jfi-cloud-up-o"></i></div><div class="jFiler-input-text"><h3>Drag&Drop files here</h3> <span style="display:inline-block; margin: 15px 0">or</span></div><a class="jFiler-input-choose-btn blue">Browse Files</a></div></div>',
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
