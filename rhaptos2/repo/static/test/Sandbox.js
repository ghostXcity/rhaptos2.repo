
// <!--
// Copyright (c) Rice University 2012-3
// This software is subject to
// the provisions of the GNU Affero General
// Public License Version 3 (AGPLv3).
// See LICENCE.txt for details.
// -->


(function() {
  var _this = this;

  define('Sandbox', ['jquery', 'app/models', 'app/views', 'test/routes', 'css!app'], function($, Models, Views, MOCK_CONTENT) {
    var metadataModal, metadataView, model, rolesModal, rolesView;
    model = new Models.Content();
    model.set(MOCK_CONTENT);
    metadataView = new Views.MetadataEditView({
      model: model
    });
    rolesView = new Views.RolesEditView({
      model: model
    });
    metadataModal = new Views.ModalWrapper(metadataView, 'Edit Metadata (test)');
    rolesModal = new Views.ModalWrapper(rolesView, 'Edit Roles (test)');
    model.on('sync', function() {
      console.log('Model Saved!', this);
      return alert("Model Saved!\n" + (JSON.stringify(this)));
    });
    $('.show-metadata').on('click', function() {
      return metadataModal.show();
    });
    return $('.show-roles').on('click', function() {
      return rolesModal.show();
    });
  });

}).call(this);

