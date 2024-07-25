***This readme is a work in progress***

<b><font size="+5">BEV Localization</font></b>
<br>

<b><font size="+3">Directories</font></b>
<br>

<details>
    <summary><b><font size="+2">attempt_at_superglue</font></b></summary>
        <font size="+2">Overlook</font><br>
            This directory contains code for operating the superglue image matcher to match drone imagery to satellite pictures for localization. Code is located in the attempt_at_superglue/src/ directory.
            <br>
            <br>
        <font size="+2">Usage</font><br>
            Running this wildnav or tester can be be done simply by following the wildnav readme. However setting it up with your own data from google earth takes a few more steps

1. In the folder generate_images you will run workflow.py
    - running workflow.py requires three parser arguements the latitude of a centralized coordinates, the longitude of a centralized coordinate, and the size in meters around the center coordinate to be covered
    - The program will provide the rest of the information for completing this step

2. Copy all files from the */generate_images/crops/ folder into */attempt_at_superglue/assets/map/ directory

3. Add a query image to */attempt_at_superglue/assets/query/

4. Edit */attempt_at_superglue/assets/query/photo_metadata.csv to suit your needs

5. run wildnav or tester

</details>
<br>

---

<details>
    <summary><b><font size="+2">descriptor_matching</font></b></summary>
        <font size="+2">Overlook</font><br>
            This directory contains code for attempting feature matching using SIFT descriptors. Using this method involves creating a *.db file of descriptors pulled from segments of a train image to be compared against descriptors from a query match. FLANN is then used to determine the best matches.
            <br>
            <br>
        <font size="+2">Programs</font><br>
            <details>
                <summary><font size="+1">create_decriptor_data_base.py</font><br></summary>
                    <h4>Required Parser Arguments</h4>
                    <ul>
                        <li><code>--image_path &lt;argv&gt;</code> The <b>str</b> path of the train image</li>
                        <li><code>--subregion_size &lt;argv&gt;</code> The <b>int</b> side size of each square subregion; <i>Defaults to 25</i></li>
                        <li><code>--step &lt;argv&gt;</code> The <b>int</b> step size between each subregion; <i>Defaults to 1</i></li>
                        <li><code>--db_name &lt;argv&gt;</code> The <b>str</b> file path of the *.db file to be saved to</li>
                    </ul>
                    <h4>Output</h4>
                    <p>A *.db file containing descriptor information for the user-submitted train image.</p>
                    <h4>Example usage</h4>
                    <pre>python3 create_descriptor_data_base.py --image_path &lt;image path&gt; --subregion_size &lt;int pixel size&gt; --step &lt;int step size&gt; --db_name &lt;intended save path&gt;</pre>
            </details>
            <br>
            <br>
            <details>
                <summary><font size="+1">create_decriptor_data_base.py</font><br></summary>
                    <h4>Required Parser Arguments</h4>
                    <ul>
                        <li><code>--query_file_path &lt;argv&gt;</code> The <b>str</b> file path of the query image</li>
                        <li><code>--db_name &lt;argv&gt;</code> The <b>str</b> file path to the *.db file that will be getting matched to</li>
                        <li><code>--train_file_path &lt;argv&gt;</code> The <b>str</b> path of the train file the database was created from</li>
                        <li><code>--output_path &lt;argv&gt;</code> The <b>str</b> path of the intended output</li>
                    </ul>
                    <h4>Optional Parser Arguments</h4>
                    <ul>
                        <li><code>--mask_file_path &lt;argv&gt;</code> The <b>path</b> to a mask image containing which areas to ignore keypoints from</li>
                        <li><code>--n_best_matches &lt;argv&gt;</code> The <b>int</b> number of top matches to be returned; <i>Defaults to 1</i></li>
                    </ul>
                    <h4>Output</h4>
                    <p>Will save an image displaying the best matches on the train image. Will also output to console the coordinates of those images.</p>
                    <h4>Example usage</h4>
                    <pre>python3 descriptor_matcher.py --query_file_path &lt;query image file path&gt; --db_name &lt;db file path&gt; --train_file_path &lt;train image file path&gt; --output_path &lt;intended output path&gt;<br><br>or<br><br>python3 descriptor_matcher.py --query_file_path &lt;query image file path&gt; --db_name &lt;db file path&gt; --train_file_path &lt;train image file path&gt; --output_path &lt;intended output path&gt; --mask_file_path &lt;mask image file path&gt; --n_best_matches &lt;number of best matches&gt;</pre>
            </details>
            <br>
            <br>
        <font size="+2">Subdirectories</font><br>
            <details>
                <summary><b><font size="+1">GUIs</font></b></summary>
                    <font size="+1">Summary</font><br>
                        This directory contains GUIs to be used in the process of gathering and prepping the images to be masked.
                        <br>
                        <br>
                        <details>
                            <summary><b><font size="+1">frame_extractor.py</font></b></summary>
                                <font size="+1">Summary</font><br>
                                    Upon running the program users will be greeted by a GUI with the ability to navigate and select a file by selecting the button titled "Browse". Once a file is selected, there is a textbox that will be pre-populated with "1.0", this number referes to the number of frames per second a user may want to extract. Once a satisfying number is selected, the user will select the button labeled "Extract frames". A popup will appear once the frames are extracted and the user may then close the windows.
                        </details>
                        <br>
                        <br>
                        <details>
                            <summary><b><font size="+1">hand_mask.py</font></b></summary>
                                <font size="+1">Summary</font><br>
                                    Upon running the program the user will be met with a screen with one available button "Load Image". Users will select this button and open an image. The user will then draw polygons around unwanted areas by hitting left click. When a polygon should be completed, the user will hit right click. Once all areas are traced, the user may select the "Save Mask" button in the bottom left corner of the image. After saving the mask, the user make then select a new image or exit the program.
                        </details>
            </details>
</details>
<br>

---

<details>
    <summary><b><font size="+2">fourier_template_matching</font></b></summary>
    <font size="+2">Summary</font><br>
        This directory contains code for template matchin using fourier transfroms. Takes a template and source image than compares the sin and cosine waves of each returning a heatmap that displays best estimated matches.
        <details>
            <summary><font size="+1">fourier_transform.py</font><br></summary>
                <h4>Required Parser Arguments</h4>
                <ul>
                    <li><code>--source_img &lt;argv&gt;</code> The <b>str</b> file path of the source image</li>
                    <li><code>--template_img &lt;argv&gt;</code> The <b>str</b> file path of the template image</li>
                    <li><code>--num_peaks &lt;argv&gt;</code> The <b>int</b> number of best matches to be found</li>
                    <li><code>--rotation_angle &lt;argv&gt;</code> The <b>int</b> angle in degrees to rotate the template image</li>
                    <li><code>--scale_factor &lt;argv&gt;</code> The <b>int</b> pixel scale difference between the source and template images</li>
                </ul>
                <h4>Output</h4>
                <p>Will output three images; One being a heatmap display where the best matches were found at; One being a an image with rectangles representing the found matched; One being the fourier transform image of template. All images will be output in the output folder</p>
                <h4>Example usage</h4>
                <pre>python3 fourier_transform.py --source_img &lt;source file path&gt; --template_img &lt;template file path&gt; --num_peaks &lt;int num peaks&gt; --rotation_angle &lt;degree rotation angel&gt; --scale_factor &lt;image scale difference&gt;</pre>
        </details>
        <br>
        <br>

</details>
<br>

---

<details>
    <summary><b><font size="+2">generate_images</font></b></summary>
        <font size="+2">Summary</font><br>
        This folder contains programs for generating different types of images and related file types
        <details>
            <summary><font size="+1">pano_to_planar_frames.py</font><br></summary>
                <h4>Required Parser Arguments</h4>
                <ul>
                    <li><code>--pano_path &lt;argv&gt;</code> The <b>str</b> file path of the panoramic image</li>
                    <li><code>--output_folder &lt;argv&gt;</code> The <b>str</b> file path of the intended output folder</li>
                </ul>
                <h4>Optional Parser Arguments</h4>
                <ul>
                    <li><code>--intended_result_frames &lt;argv&gt;</code> The <b>int</b> number of frames to be output (max 1440); <i>Defaults to 1</i></li>
                    <li><code>--FOV &lt;argv&gt;</code> The <b>int</b> FOV that the pano was taken at; <i>Defaults to 160</i></li>
                    <li><code>--output_size &lt;argv&gt;</code> The <b>tuple</b> pixel size of the intended output image; <i>Defaults to (608, 608)</i></li>
                    <li><code>--pitch &lt;argv&gt;</code> The <b>int</b> pitch angle for the output frames in degrees; <i>Defaults to 180</i></li>
                </ul>
                <h4>Output</h4>
                <p>A folder containing the number of specified planar frames extracted from a 360 panoramic image</p>
                <h4>Example usage</h4>
                <pre>python3 fourier_transform.py --pano_path &lt;panoramic file path&gt; --output_folder &lt;output folder file path&gt;<br><br>or<br><br>python3 --pano_path &lt;panoramic file path&gt; --output_folder &lt;output folder file path&gt; --intended_result_frames &lt;num result frames&gt; --FOV &lt;pano FOV&gt; --output_size &lt;tuple output size&gt; --pitch &lt;pitch angle&gt;</pre>
        </details>
        <br>
        <br>
        <details>
            <summary><font size="+1">stitch_images.py</font><br></summary>
                <h4>Required Parser Arguments</h4>
                <ul>
                    <li><code>--input_folder &lt;argv&gt;</code> The <b>str</b> file path of the folder containing images to be stitched</li>
                    <li><code>--output_folder &lt;argv&gt;</code> The <b>str</b> file path of the intended output folder</li>
                </ul>
                <h4>Required Parser Arguments</h4>
                <ul>
                    <li><code>--stitch_type &lt;argv&gt;</code> The <b>str</b> stitch type, options are "PANORAMA" or "SCANS"</li>
                </ul>
                <h4>Output</h4>
                <p>Will output three images; One being a heatmap display where the best matches were found at; One being a an image with rectangles representing the found matched; One being the fourier transform image of template. All images will be output in the output folder</p>
                <h4>Example usage</h4>
                <pre>python3 fourier_transform.py --input_folder &lt;input folder path&gt; --output_folder &lt;output folder file path&gt;<br><br>or<br><br>python3 fourier_transform.py --input_folder &lt;input folder path&gt; --output_folder &lt;output folder file path&gt; --stitch_type &lt;"PANORAMA" or "SCANS"&gt;</pre>
        </details>
        <br>
        <br>
        <details>
            <summary><font size="+1">kml_workflow.py</font><br></summary>
                This program requires its user to have access to the google earth pro application.
                <h4>Required Parser Arguments</h4>
                <ul>
                    <li><code>--center_lat &lt;argv&gt;</code> The <b>float</b> lat that the KML will be centered at</li>
                    <li><code>--center_lon &lt;argv&gt;</code> The <b>float</b> lon that the KML will be centered at</li>
                    <li><code>--size_meters &lt;argv&gt;</code> The <b>int</b> total side length of the bounding box created by the KML</li>
                </ul>
                <h4>Output</h4>
                <p>Will output a KML file and a screenshot image of a location from google earth pro</p>
                <h4>Example usage</h4>
                <pre>python3 fourier_transform.py --center_lat &lt;latitude&gt; --center_lon &lt;longitude&gt; --size_meters &lt;bounding box length&gt;</pre>
        </details>
        <br>
        <br>
</details>


