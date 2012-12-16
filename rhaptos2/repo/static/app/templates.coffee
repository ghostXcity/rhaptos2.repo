# This file should no longer be used...
define [], ->
  # Export the templates so they can be used by other modules
  templates = {}

  templates.IMPORT = '
    <div role="popup-content">
      <input type="hidden" name="id" value="{{id}}">
      <input type="file" name="file">
    </div>'

  templates.SHARING = '
    <div role="popup-content">
      <form name="sharing-form" action="sharing" method="POST">
        <legend>Sharing Assignments</legend>
        <!-- The role to user listing table -->
        <table class="table table-condensed">
          <thead>
            <tr>
              <th></th>
              <th>Owner</th>
              <th>Editor</th>
              <th>Reviewer</th>
              <th><!-- Other actions --></th>
            </tr>
          </thead>
          <tfoot>
          </tfoot>
          <tbody>
            <tr>
              <th>Michael</th>
              <td><input type="checkbox" name="role" value="uid"></td>
              <td>
                <button type="button"
                        class="btn btn-danger btn-mini">remove</button>
              </td>
            </tr>
            <tr>
              <th>Ross</th>
              <td><input type="checkbox" name="role" value="uid"></td>
              <td><input type="checkbox" name="role" value="uid"></td>
              <td>
                <button type="button"
                        class="btn btn-danger btn-mini">remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </form>
      <form name="sharing-search-form">
        <legend>Search for people</legend>

        <div id="sharing-search-form-results">
          <!-- A search for the letter "a" -->
          <span class="user-result badge badge-info" data-uid="uid">Isabel</span>
          <!-- Michael shows up in the search results but is disabled --
            -- since he is already in the list. -->
          <span class="user-result badge" data-uid="uid">Michael</span>
          <span class="user-result badge badge-info" data-uid="uid">Paul</span>
        </div>

        <div class="input-append">
          <input type="text" name="q"
                 class="span2"
                 placeholder="Type a name...">
          <button type="submit" class="btn">Search</button>
        </div>
      </form>
    </div>'

  templates.PUBLISH = '
    <div role="popup-content">
      <form name="publish-form" action="publish" method="POST">
        <legend>Description of the changes</legend>
        <input type="text" name="change_description"
               class="span4"
               placeholder="Description of the change...">
        <legend>License</legend
        <div>
          <p>This work will now be distributed under the terms of the Creative Commons Attribution License (<span>CC-BY 3.0</span>) available at <a style="font-style: italic" href="http://creativecommons.org/licenses/by/3.0/">http://creativecommons.org/licenses/by/3.0/</a>.
          </p>
          <p>By publishing this content you area to the following statement: I understand that in doing so I</p>
          <ol>
            <li>retain my copyright in the work and</li>
            <li>warrant that I am the author or the owner or have permission to distribute the work in question and</li>
            <li>wish this work to be distributed under the terms of the CC-BY 3.0 license (including allowing modification of this work and requiring attribution) and</li>
            <li>agree that proper attribution of my work is any attribution that includes the authors\' names, the title of the work, and the Connexions URL to the work.</li>
          </ol>
        </div>
      </form>
    </div>'

  # Export the templates so they can be used by other modules
  @Templates = templates
  return templates
