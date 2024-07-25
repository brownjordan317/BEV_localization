***This readme is a work in progress***

# BEV Localization

## Directories

<details>
    <summary><b><font size="+2">attempt_at_superglue</font></b></summary>
    <h3>Overlook</h3>
    <p>This directory contains code for operating the SuperGlue image matcher to match drone imagery to satellite pictures for localization. Code is located in the <code>attempt_at_superglue/src/</code> directory.</p>
    
    <h3>Usage</h3>
    <p>Running this WildNav or tester can be done simply by following the WildNav README. However, setting it up with your own data from Google Earth takes a few more steps:</p>

    1. In the folder <code>generate_images</code>, run <code>workflow.py</code>
        - Running <code>workflow.py</code> requires three parser arguments: the latitude of a centralized coordinate, the longitude of a centralized coordinate, and the size in meters around the center coordinate to be covered.
        - The program will provide the rest of the information for completing this step.
    2. Copy all files from the <code>generate_images/crops/</code> folder into the <code>attempt_at_superglue/assets/map/</code> directory.
    3. Add a query image to <code>attempt_at_superglue/assets/query/</code>.
    4. Edit <code>attempt_at_superglue/assets/query/photo_metadata.csv</code> to suit your needs.
    5. Run WildNav or tester.
</details>

---

<details>
    <summary><b><font size="+2">descriptor_matching</font></b></summary>
    <h3>Overlook</h3>
    <p>This directory contains code for attempting feature matching using SIFT descriptors. Using this method involves creating a <code>*.db</code> file of descriptors pulled from segments of a train image to be compared against descriptors from a query match. FLANN is then used to determine the best matches.</p>
    <h3>Programs</h3>
    <details>
        <summary><font size="+1">create_descriptor_database.py</font></summary>
        <h4>Required Parser Arguments</h4>
        <ul>
            <li><code>--image_path &lt;argv&gt;</code>: The <b>str</b> path of the train image.</li>
            <li><code>--subregion_size &lt;argv&gt;</code>: The <b>int</b> side size of each square subregion; <i>Defaults to 25</i>.</li>
            <li><code>--step &lt;argv&gt;</code>: The <b>int</b> step size between each subregion; <i>Defaults to 1</i>.</li>
            <li><code>--db_name &lt;argv&gt;</code>: The <b>str</b> file path of the <code>*.db</code> file to be saved to.</li>
        </ul>
        <h4>Output</h4>
        <p>A <code>*.db</code> file containing descriptor information for the user-submitted train image.</p>
        <h4>Example Usage</h4>
        <pre>python3 create_descriptor_database.py --image_path &lt;image path&gt; --subregion_size &lt;int pixel size&gt; --step &lt;int step size&gt; --db_name &lt;intended save path&gt;</pre>
    </details>
    <br>
    <details>
        <summary><font size="+1">descriptor_matcher.py</font></summary>
        <h4>Required Parser Arguments</h4>
        <ul>
            <li><code>--query_file_path &lt;argv&gt;</code>: The <b>str</b> file path of the query image.</li>
            <li><code>--db_name &lt;argv&gt;</code>: The <b>str</b> file path to the <code>*.db</code> file that will be matched to.</li>
            <li><code>--train_file_path &lt;argv&gt;</code>: The <b>str</b> path of the train file the database was created from.</li>
            <li><code>--output_path &lt;argv&gt;</code>: The <b>str</b> path of the intended output.</li>
        </ul>
        <h4>Optional Parser Arguments</h4>
        <ul>
            <li><code>--mask_file_path &lt;argv&gt;</code>: The <b>path</b> to a mask image containing areas to ignore keypoints from.</li>
            <li><code>--n_best_matches &lt;argv&gt;</code>: The <b>int</b> number of top matches to be returned; <i>Defaults to 1</i>.</li>
        </ul>
        <h4>Output</h4>
        <p>Will save an image displaying the best matches on the train image. It will also output to the console the coordinates of those matches.</p>
        <h4>Example Usage</h4>
        <pre>python3 descriptor_matcher.py --query_file_path &lt;query image file path&gt; --db_name &lt;db file path&gt; --train_file_path &lt;train image file path&gt; --output_path &lt;intended output path&gt;</pre>
        <p>or</p>
        <pre>python3 descriptor_matcher.py --query_file_path &lt;query image file path&gt; --db_name &lt;db file path&gt; --train_file_path &lt;train image file path&gt; --output_path &lt;intended output path&gt; --mask_file_path &lt;mask image file path&gt; --n_best_matches &lt;number of best matches&gt;</pre>
    </details>
    <br>
    <h3>Subdirectories</h3>
    <details>
        <summary><b><font size="+1">GUIs</font></b></summary>
        <h4>Summary</h4>
        <p>This directory contains GUIs to be used in the process of gathering and prepping the images to be masked.</p>
        <br>
        <details>
            <summary><b><font size="+1">frame_extractor.py</font></b></summary>
            <h4>Summary</h4>
            <p>Upon running the program, users will be greeted by a GUI with the ability to navigate and select a file by selecting the button titled "Browse". Once a file is selected, there is a textbox that will be pre-populated with "1.0". This number refers to the number of frames per second a user may want to extract. Once a satisfying number is selected, the user will select the button labeled "Extract frames". A popup will appear once the frames are extracted and the user may then close the windows.</p>
        </details>
        <br>
        <details>
            <summary><b><font size="+1">hand_mask.py</font></b></summary>
            <h4>Summary</h4>
            <p>Upon running the program, the user will be met with a screen with one available button, "Load Image". Users will select this button and open an image. The user will then draw polygons around unwanted areas by hitting left click. When a polygon should be completed, the user will hit right click. Once all areas are traced, the user may select the "Save Mask" button in the bottom left corner of the image. After saving the mask, the user may then select a new image or exit the program.</p>
        </details>
    </details>
</details>

---

<details>
    <summary><b><font size="+2">fourier_template_matching</font></b></summary>
    <h3>Summary</h3>
    <p>This directory contains code for template matching using Fourier transforms. It takes a template and source image and compares the sine and cosine waves of each, returning a heatmap that displays the best estimated matches.</p>
    <details>
        <summary><font size="+1">fourier_transform.py</font></summary>
        <h4>Required Parser Arguments</h4>
        <ul>
            <li><code>--source_img &lt;argv&gt;</code>: The <b>str</b> file path of the source image.</li>
            <li><code>--template_img &lt;argv&gt;</code>: The <b>str</b> file path of the template image.</li>
            <li><code>--num_peaks &lt;argv&gt;</code>: The <b>int</b> number of best matches to be found.</li>
            <li><code>--rotation_angle &lt;argv&gt;</code>: The <b>int</b> angle in degrees to rotate the template image.</li>
            <li><code>--scale_factor &lt;argv&gt;</code>: The <b>int</b> pixel scale difference between the source and template images.</li>
        </ul>
        <h4>Output</h4>
        <p>Will output three images: one being a heatmap display where the best matches were found, one being an image with rectangles representing the found matches, and one being the Fourier transform image of the template. All images will be output in the output folder.</p>
        <h4>Example Usage</h4>
        <pre>python3 fourier_transform.py --source_img &lt;source file path&gt; --template_img &lt;template file path&gt; --num_peaks &lt;int num peaks&gt; --rotation_angle &lt;degree rotation angle&gt; --scale_factor &lt;image scale difference&gt;</pre>
    </details>
</details>

---

<details>
    <summary><b><font size="+2">generate_images</font></b></summary>
    <h3>Summary</h3>
    <p>This folder contains programs for generating different types of images and related file types.</p>
    <details>
        <summary><font size="+1">pano_to_planar_frames.py</font></summary>
        <h4>Required Parser Arguments</h4>
        <ul>
            <li><code>--pano_path &lt;argv&gt;</code>: The <b>str</b> file path of the panoramic image.</li>
            <li><code>--output_folder &lt;argv&gt;</code>: The <b>str</b> file path of the intended output folder.</li>
        </ul>
        <h4>Optional Parser Arguments</h4>
        <ul>
            <li><code>--intended_result_frames &lt;argv&gt;</code>: The <b>int</b> number of frames to be output (max 1440); <i>Defaults to 1</i>.</li>
            <li><code>--FOV &lt;argv&gt;</code>: The <b>int</b> FOV that the pano was taken at; <i>Defaults to 160</i>.</li>
            <li><code>--output_size &lt;argv&gt;</code>: The <b>tuple</b> pixel size of the intended output image; <i>Defaults to (608, 608)</i>.</li>
            <li><code>--pitch &lt;argv&gt;</code>: The <b>int</b> pitch angle for the output frames in degrees; <i>Defaults to 180</i>.</li>
        </ul>
        <h4>Output</h4>
        <p>A folder containing the specified number of planar frames extracted from a 360 panoramic image.</p>
        <h4>Example Usage</h4>
        <pre>python3 pano_to_planar_frames.py --pano_path &lt;panoramic file path&gt; --output_folder &lt;output folder file path&gt;</pre>
        <p>or</p>
        <pre>python3 pano_to_planar_frames.py --pano_path &lt;panoramic file path&gt; --output_folder &lt;output folder file path&gt; --intended_result_frames &lt;num result frames&gt; --FOV &lt;pano FOV&gt; --output_size &lt;tuple output size&gt; --pitch &lt;pitch angle&gt;</pre>
    </details>
    <br>
    <details>
        <summary><font size="+1">stitch_images.py</font></summary>
        <h4>Required Parser Arguments</h4>
        <ul>
            <li><code>--input_folder &lt;argv&gt;</code>: The <b>str</b> file path of the folder containing images to be stitched.</li>
            <li><code>--output_folder &lt;argv&gt;</code>: The <b>str</b> file path of the intended output folder.</li>
        </ul>
        <h4>Optional Parser Arguments</h4>
        <ul>
            <li><code>--stitch_type &lt;argv&gt;</code>: The <b>str</b> stitch type; options are "PANORAMA" or "SCANS".</li>
        </ul>
        <h4>Output</h4>
        <p>A stitched image from the input folder images.</p>
        <h4>Example Usage</h4>
        <pre>python3 stitch_images.py --input_folder &lt;input folder path&gt; --output_folder &lt;output folder file path&gt;</pre>
        <p>or</p>
        <pre>python3 stitch_images.py --input_folder &lt;input folder path&gt; --output_folder &lt;output folder file path&gt; --stitch_type &lt;"PANORAMA" or "SCANS"&gt;</pre>
    </details>
    <br>
    <details>
        <summary><font size="+1">kml_workflow.py</font></summary>
        <p>This program requires its user to have access to the Google Earth Pro application.</p>
        <h4>Required Parser Arguments</h4>
        <ul>
            <li><code>--center_lat &lt;argv&gt;</code>: The <b>float</b> latitude that the KML will be centered at.</li>
            <li><code>--center_lon &lt;argv&gt;</code>: The <b>float</b> longitude that the KML will be centered at.</li>
            <li><code>--size_meters &lt;argv&gt;</code>: The <b>int</b> total side length of the bounding box created by the KML.</li>
        </ul>
        <h4>Output</h4>
        <p>A KML file and a screenshot image of a location from Google Earth Pro.</p>
        <h4>Example Usage</h4>
        <pre>python3 kml_workflow.py --center_lat &lt;latitude&gt; --center_lon &lt;longitude&gt; --size_meters &lt;bounding box length&gt;</pre>
    </details>
</details>


