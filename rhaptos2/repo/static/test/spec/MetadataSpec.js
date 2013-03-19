
// <!--
// Copyright (c) Rice University 2012-3
// This software is subject to
// the provisions of the GNU Affero General
// Public License Version 3 (AGPLv3).
// See LICENCE.txt for details.
// -->


(function() {

  define(['app/models', 'app/views', 'test/routes'], function(Models, Views, MOCK_CONTENT) {
    return describe('Edit Metadata/Roles', function() {
      beforeEach(function() {
        this.model = new Models.Content();
        this.model.set(MOCK_CONTENT);
        this.metadataView = new Views.MetadataEditView({
          model: this.model
        });
        this.rolesView = new Views.RolesEditView({
          model: this.model
        });
        this.metadataModal = new Views.ModalWrapper(this.metadataView, 'Edit Metadata (test)');
        return this.rolesModal = new Views.ModalWrapper(this.rolesView, 'Edit Roles (test)');
      });
      return describe('(Sanity Check) All Views', function() {
        it('should have a .$el', function() {
          expect(this.metadataView.$el).not.toBeFalsy();
          expect(this.rolesView.$el).not.toBeFalsy();
          expect(this.metadataModal.view).not.toBeFalsy();
          return expect(this.rolesModal.view).not.toBeFalsy();
        });
        it('should initially be hidden', function() {
          return expect(this.metadataView.$el.is(':visible')).toEqual(false);
        });
        return it('should show without errors', function() {
          expect(this.metadataModal.show.bind(this.metadataModal)).not.toThrow();
          expect(this.metadataModal.hide.bind(this.metadataModal)).not.toThrow();
          expect(this.rolesModal.show.bind(this.rolesModal)).not.toThrow();
          return expect(this.rolesModal.hide.bind(this.rolesModal)).not.toThrow();
        });
      });
    });
  });

}).call(this);

